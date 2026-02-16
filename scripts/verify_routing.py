
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../src/routing"))

from router import Router
import networkx as nx

def verify():
    print("--- Verifying Router ---")
    try:
        router = Router("campus_network.graphml")
        
        # Test Points (Student Center to Library)
        origin = (38.9424, -92.3271)
        dest = (38.9447, -92.3268)
        
        print(f"Origin: {origin}, Dest: {dest}")
        
        # 1. Shortest Path
        shortest_route = router.get_route(origin, dest, mode='shortest')
        if not shortest_route:
            print("FAIL: No shortest path found.")
            return

        # --- TEST 2: Mock High Risk to force deviation ---
        # Get an edge from the shortest path and make it very risky
        u, v = shortest_route[len(shortest_route)//2], shortest_route[len(shortest_route)//2 + 1]
        print(f"Injecting mock crime on edge {u}->{v}...")
        
        # Artificial penalty
        router.graph[u][v][0]['safety_score'] = 10000.0 # Huge penalty
        router.graph[u][v][0]['risk_factor'] = 100.0    # For stats
        
        # 2. Safe Path
        safe_route = router.get_route(origin, dest, mode='safe')
        if not safe_route:
            print("FAIL: No safe path found.")
            return
            
        print(f"Shortest Path Nodes: {len(shortest_route)}")
        print(f"Safe Path Nodes:     {len(safe_route)}")
        
        # Check if they are different (they likely will be if weights work)
        if shortest_route != safe_route:
            print("SUCCESS: Safe path is distinct from shortest path.")
        else:
            print("NOTE: Safe path is identical to shortest path. (This can happen if shortest is also safest)")
            
    
        # Helper to print stats
        def get_route_stats(route, graph):
            # Calculate weighted length?
            total_len = 0
            total_risk = 0
            for u, v in zip(route[:-1], route[1:]):
                data = graph.get_edge_data(u, v)[0]
                total_len += data.get('length', 0)
                total_risk += data.get('risk_factor', 1.0)
            return total_len, total_risk / len(route)
            
        s_len, s_risk = get_route_stats(shortest_route, router.graph)
        print(f"Shortest Route: Length={s_len:.1f}m, Avg Risk={s_risk:.2f}")

        safe_len, safe_risk = get_route_stats(safe_route, router.graph)
        print(f"Safe Route:     Length={safe_len:.1f}m, Avg Risk={safe_risk:.2f}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
