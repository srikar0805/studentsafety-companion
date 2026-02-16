
import osmnx as ox
import networkx as nx
import pickle

class Router:
    def __init__(self, graph_path="campus_network.graphml"):
        print(f"Loading graph from {graph_path}...")
        self.graph = ox.load_graphml(graph_path)
        print("Graph loaded.")
        
        # Ensure numerical types
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            if 'length' in data:
                data['length'] = float(data['length'])
            if 'safety_score' in data:
                data['safety_score'] = float(data['safety_score'])
            if 'risk_factor' in data:
                data['risk_factor'] = float(data['risk_factor'])

    def get_route(self, origin_coords, dest_coords, mode='safe'):
        """
        Calculates route between (lat, lon) tuples.
        mode: 'shortest' (distance) or 'safe' (safety_score)
        """
        # Project input (lat/lon) to graph CRS (meters)
        # Graph CRS is stored as string 'EPSG:32615' or similar.
        graph_crs = self.graph.graph['crs']
        
        # Create GeoDataFrame with WGS84 points
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Geometry: Point(lon, lat)
        points = gpd.GeoDataFrame(
            geometry=[Point(origin_coords[1], origin_coords[0]), Point(dest_coords[1], dest_coords[0])], 
            crs="EPSG:4326"
        )
        
        # Project
        points_proj = points.to_crs(graph_crs)
        
        orig_x = points_proj.geometry.iloc[0].x
        orig_y = points_proj.geometry.iloc[0].y
        dest_x = points_proj.geometry.iloc[1].x
        dest_y = points_proj.geometry.iloc[1].y

        # Find nearest nodes
        orig_node = ox.distance.nearest_nodes(self.graph, orig_x, orig_y)
        dest_node = ox.distance.nearest_nodes(self.graph, dest_x, dest_y)
        
        weight = 'length' if mode == 'shortest' else 'safety_score'
        
        try:
            route = nx.shortest_path(self.graph, orig_node, dest_node, weight=weight)
            return route
        except nx.NetworkXNoPath:
            print("No path found.")
            return None

    def route_to_coords(self, route):
        """Converts node IDs to [(lat, lon), ...]"""
        coords = []
        for node in route:
            pt = self.graph.nodes[node]
            coords.append((pt['y'], pt['x']))
        return coords

if __name__ == "__main__":
    # Test
    # Student Center: 38.9424, -92.3271
    # Library: 38.9447, -92.3268
    router = Router()
    print("Calculating Safe Route...")
    safe_route = router.get_route((38.9424, -92.3271), (38.9447, -92.3268), mode='safe')
    print(f"Safe Route Nodes: {len(safe_route)}")
    
    print("Calculating Shortest Route...")
    short_route = router.get_route((38.9424, -92.3271), (38.9447, -92.3268), mode='shortest')
    print(f"Shortest Route Nodes: {len(short_route)}")
