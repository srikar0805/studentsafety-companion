
import os
import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from shapely.geometry import Point, LineString
from sklearn.neighbors import BallTree
import numpy as np
import pickle
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONN = os.getenv("DATABASE_URL")
PLACE_NAME = "Columbia, Missouri, USA"
GRAPH_PATH = "campus_network.graphml"

class SafetyGraph:
    def __init__(self, db_conn=DB_CONN):
        self.engine = create_engine(db_conn)
        self.graph = None
        self.gdf_nodes = None
        self.gdf_edges = None

    def build_graph(self, place=PLACE_NAME):
        """Downloads walkable street network from OSM."""
        print(f"Downloading graph for {place}...")
        # 'walk' network type gets sidewalks and paths
        self.graph = ox.graph_from_place(place, network_type='walk')
        # Project to UTM (meters) for accurate distance/buffer checks
        self.graph = ox.project_graph(self.graph)
        print("Graph downloaded and projected.")
        
        # Convert to GeoDataFrames for spatial ops
        self.gdf_nodes, self.gdf_edges = ox.graph_to_gdfs(self.graph)

    def load_safety_data(self):
        """Fetches assets (safe) and crimes (risky) from DB."""
        print("Loading safety data from DB...")
        
        # 1. Safety Assets (Phones, Entrances) -> Positive weight (reduction in cost)
        assets_query = "SELECT asset_type, description, ST_X(location_geo::geometry) as lon, ST_Y(location_geo::geometry) as lat FROM safety_assets"
        self.df_assets = pd.read_sql(assets_query, self.engine)
        
        # 2. Crimes (MUPD + CPD) -> Negative weight (increase in cost)
        # Recent crimes (last year?) maybe weight by recency. For MVP, just all.
        crimes_query = """
            SELECT incident_type, ST_X(location_geo::geometry) as lon, ST_Y(location_geo::geometry) as lat 
            FROM crime_incidents WHERE location_geo IS NOT NULL
            UNION ALL
            SELECT nibrs_description as incident_type, ST_X(location_geo::geometry) as lon, ST_Y(location_geo::geometry) as lat 
            FROM cpd_incidents WHERE location_geo IS NOT NULL
        """
        self.df_crimes = pd.read_sql(crimes_query, self.engine)
        
        # Convert to GeoDataFrames and project to match Graph (UTM)
        # Assuming Data is WGS84 (4326)
        if not self.df_assets.empty:
            self.gdf_assets = gpd.GeoDataFrame(
                self.df_assets, 
                geometry=gpd.points_from_xy(self.df_assets.lon, self.df_assets.lat),
                crs="EPSG:4326"
            ).to_crs(self.graph.graph['crs'])
        else:
            self.gdf_assets = gpd.GeoDataFrame()

        if not self.df_crimes.empty:
            self.gdf_crimes = gpd.GeoDataFrame(
                self.df_crimes, 
                geometry=gpd.points_from_xy(self.df_crimes.lon, self.df_crimes.lat),
                crs="EPSG:4326"
            ).to_crs(self.graph.graph['crs'])
        else:
            self.gdf_crimes = gpd.GeoDataFrame()
            
        print(f"Loaded {len(self.gdf_assets)} assets and {len(self.gdf_crimes)} crimes.")

    def calculate_risk_scores(self):
        """
        Iterates over edges.
        Adjusts 'safety_weight' based on proximity to assets (-) and crimes (+).
        Base weight is length (meters).
        """
        print("Calculating risk scores...")
        
        # Weights
        # Asset benefit: reduce effective distance by 20% if within 50m
        # Crime penalty: increase effective distance by 50% if within 100m
        
        # Build Spatial Indices for fast lookup
        asset_tree = None
        crime_tree = None
        
        if not self.gdf_assets.empty:
            asset_coords = np.array(list(zip(self.gdf_assets.geometry.x, self.gdf_assets.geometry.y)))
            asset_tree = BallTree(asset_coords, metric='euclidean')
            
        if not self.gdf_crimes.empty:
            crime_coords = np.array(list(zip(self.gdf_crimes.geometry.x, self.gdf_crimes.geometry.y)))
            crime_tree = BallTree(crime_coords, metric='euclidean')
            
        # Iterate Edges
        # ox edges are (u, v, key, data)
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            length = data.get('length', 1.0)
            
            # Use midpoint of edge for proximity check
            # Nodes u, v have 'x', 'y' in projected crs
            pt_u = self.graph.nodes[u]
            pt_v = self.graph.nodes[v]
            mid_x = (pt_u['x'] + pt_v['x']) / 2
            mid_y = (pt_u['y'] + pt_v['y']) / 2
            
            # --- Safety Factor ---
            safety_factor = 1.0
            
            # Check Assets (<50m)
            if asset_tree:
                count_assets = asset_tree.query_radius([[mid_x, mid_y]], r=50, count_only=True)[0]
                if count_assets > 0:
                    safety_factor *= 0.8 # 20% reduction per asset type? Or flat? Let's do flat for now.
            
            # Check Crimes (<100m)
            if crime_tree:
                count_crimes = crime_tree.query_radius([[mid_x, mid_y]], r=100, count_only=True)[0]
                # Scale penalty by count?
                if count_crimes > 0:
                    # Logarithmic penalty? Or Linear?
                    # simple: 1.2 base + 0.05 * count
                    penalty = 1.2 + (0.05 * min(count_crimes, 10))
                    safety_factor *= penalty
            
            # Calculate final weighted length
            # If safety_factor < 1 (safer), length decreases (preferred)
            # If safety_factor > 1 (risky), length increases (avoided)
            weighted_len = float(length * safety_factor)
            
            data['safety_score'] = weighted_len
            data['risk_factor'] = float(safety_factor) # For debugging/viz
            
        print("Risk scores calculated.")

    def save_graph(self, filename=GRAPH_PATH):
        # Save as GraphML (standard)
        ox.save_graphml(self.graph, filepath=filename)
        print(f"Graph saved to {filename}")
        
    def run(self):
        self.build_graph()
        self.load_safety_data()
        self.calculate_risk_scores()
        self.save_graph()

if __name__ == "__main__":
    sg = SafetyGraph()
    sg.run()
