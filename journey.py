"""
journey.py — Fund flow journey reconstruction
DFS/BFS traversal to reconstruct full A→B→C→D path for suspicious accounts.
"""

import networkx as nx
from collections import deque


def get_outgoing_journey(G, account, cutoff=10, min_amount=None, time_window=None):
    """
    BFS to find all outgoing paths from an account.
    
    Args:
        G: NetworkX MultiDiGraph
        account: starting account ID
        cutoff: max path length
        min_amount: optional filter for minimum transaction amount
        time_window: optional tuple (start_time, end_time) to filter by timestamp
    
    Returns:
        list of paths (each path is a list of account IDs)
    """
    if account not in G:
        return []
    
    paths = []
    queue = deque([(account, [account])])
    visited = set()
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) > cutoff:
            continue
        
        # Get outgoing edges with optional filters
        for _, neighbor, data in G.out_edges(current, data=True):
            # Skip if already in path (avoid cycles in journey)
            if neighbor in path:
                continue
            
            # Apply amount filter
            if min_amount and data.get("amount", 0) < min_amount:
                continue
            
            # Apply time filter
            if time_window:
                ts = data.get("timestamp")
                if ts and not (time_window[0] <= ts <= time_window[1]):
                    continue
            
            new_path = path + [neighbor]
            paths.append(new_path)
            queue.append((neighbor, new_path))
    
    return paths


def get_incoming_journey(G, account, cutoff=10, min_amount=None, time_window=None):
    """
    BFS to find all incoming paths TO an account (reverse journey).
    
    Returns:
        list of paths (each path is a list of account IDs leading TO this account)
    """
    if account not in G:
        return []
    
    # Reverse the graph conceptually
    paths = []
    queue = deque([(account, [account])])
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) > cutoff:
            continue
        
        for neighbor, _, data in G.in_edges(current, data=True):
            if neighbor in path:
                continue
            
            if min_amount and data.get("amount", 0) < min_amount:
                continue
            
            if time_window:
                ts = data.get("timestamp")
                if ts and not (time_window[0] <= ts <= time_window[1]):
                    continue
            
            new_path = [neighbor] + path
            paths.append(new_path)
            queue.append((neighbor, new_path))
    
    return paths


def get_full_journey(G, account, cutoff=10):
    """
    Get complete journey - both incoming sources and outgoing destinations.
    
    Returns:
        dict with 'incoming' and 'outgoing' paths
    """
    return {
        "account": account,
        "incoming": get_incoming_journey(G, account, cutoff),
        "outgoing": get_outgoing_journey(G, account, cutoff),
        "in_degree": G.in_degree(account),
        "out_degree": G.out_degree(account)
    }


def find_fund_source(G, account, cutoff=5, min_amount=None):
    """
    DFS to trace back to ultimate fund sources.
    Returns paths from source accounts that have no incoming edges.
    """
    sources = []
    
    def dfs(current, path, visited):
        if len(path) > cutoff:
            return
        
        # If no incoming edges, this is a source
        if G.in_degree(current) == 0:
            sources.append(list(path))
            return
        
        for predecessor, _, data in G.in_edges(current, data=True):
            if predecessor in visited:
                continue
            
            if min_amount and data.get("amount", 0) < min_amount:
                continue
            
            visited.add(predecessor)
            path.appendleft(predecessor)
            dfs(predecessor, path, visited)
            path.popleft()
            visited.remove(predecessor)
    
    visited = {account}
    path = deque([account])
    dfs(account, path, visited)
    
    return sources


def find_fund_destination(G, account, cutoff=5, min_amount=None):
    """
    DFS to trace forward to ultimate fund destinations.
    Returns paths to destination accounts that have no outgoing edges.
    """
    destinations = []
    
    def dfs(current, path, visited):
        if len(path) > cutoff:
            return
        
        # If no outgoing edges, this is a destination
        if G.out_degree(current) == 0:
            destinations.append(list(path))
            return
        
        for _, successor, data in G.out_edges(current, data=True):
            if successor in visited:
                continue
            
            if min_amount and data.get("amount", 0) < min_amount:
                continue
            
            visited.add(successor)
            path.append(successor)
            dfs(successor, path, visited)
            path.pop()
            visited.remove(successor)
    
    visited = {account}
    path = [account]
    dfs(account, path, visited)
    
    return destinations


def trace_specific_path(G, source, target, cutoff=10):
    """
    Find specific path(s) between two accounts using NetworkX.
    
    Returns:
        list of simple paths from source to target
    """
    try:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=cutoff))
        return paths
    except nx.NodeNotFound:
        return []
    except nx.NetworkXNoPath:
        return []


def get_transaction_chain(G, path):
    """
    Get transaction details for a path of accounts.
    
    Args:
        G: MultiDiGraph
        path: list of account IDs
    
    Returns:
        list of transaction dicts between consecutive accounts in path
    """
    if len(path) < 2:
        return []
    
    chain = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        # Get all edges between these two nodes
        edges = G.get_edge_data(u, v)
        if edges:
            for key, data in edges.items():
                chain.append({
                    "from": u,
                    "to": v,
                    **data
                })
    
    return chain


def format_path(path):
    """Format a path list as A→B→C string."""
    return " → ".join(path) if path else "(no path)"


def analyze_suspicious_journeys(G, suspicious_accounts, max_paths_per_account=3):
    """
    Analyze fund journeys for a list of suspicious accounts.
    
    Returns:
        dict mapping account_id to journey analysis
    """
    results = {}
    
    for acc in suspicious_accounts:
        if acc not in G:
            continue
        
        journey = get_full_journey(G, acc, cutoff=8)
        
        # Get transaction details for top outgoing paths
        outgoing_details = []
        for path in journey["outgoing"][:max_paths_per_account]:
            chain = get_transaction_chain(G, path)
            total_amount = sum(t.get("amount", 0) for t in chain)
            outgoing_details.append({
                "path": format_path(path),
                "hops": len(path) - 1,
                "transactions": len(chain),
                "total_amount": total_amount,
                "chain": chain
            })
        
        # Get transaction details for top incoming paths
        incoming_details = []
        for path in journey["incoming"][:max_paths_per_account]:
            chain = get_transaction_chain(G, path)
            total_amount = sum(t.get("amount", 0) for t in chain)
            incoming_details.append({
                "path": format_path(path),
                "hops": len(path) - 1,
                "transactions": len(chain),
                "total_amount": total_amount,
                "chain": chain
            })
        
        results[acc] = {
            "journeys_out": outgoing_details,
            "journeys_in": incoming_details,
            "sources": find_fund_source(G, acc, cutoff=5)[:max_paths_per_account],
            "destinations": find_fund_destination(G, acc, cutoff=5)[:max_paths_per_account]
        }
    
    return results


def print_journey_summary(journey_results, top_n=10):
    """Print formatted journey summary."""
    print("\n" + "=" * 80)
    print("FUND FLOW JOURNEY ANALYSIS")
    print("=" * 80)
    
    for i, (acc, data) in enumerate(list(journey_results.items())[:top_n], 1):
        print(f"\n{i}. Account: {acc}")
        print("-" * 60)
        
        if data["journeys_out"]:
            print("  Outgoing journeys:")
            for j in data["journeys_out"][:3]:
                print(f"    → {j['path']}")
                print(f"      ({j['hops']} hops, ₹{j['total_amount']:,.2f})")
        
        if data["journeys_in"]:
            print("  Incoming journeys:")
            for j in data["journeys_in"][:3]:
                print(f"    ← {j['path']}")
                print(f"      ({j['hops']} hops, ₹{j['total_amount']:,.2f})")
        
        if not data["journeys_out"] and not data["journeys_in"]:
            print("  (no multi-hop journeys found)")


if __name__ == "__main__":
    # Test with sample graph
    print("Testing journey module...")
    
    # Create test graph
    G = nx.MultiDiGraph()
    G.add_edge("A", "B", amount=1000, txn_id="t1")
    G.add_edge("B", "C", amount=950, txn_id="t2")
    G.add_edge("C", "D", amount=900, txn_id="t3")
    G.add_edge("A", "C", amount=500, txn_id="t4")
    
    # Test outgoing
    out_paths = get_outgoing_journey(G, "A", cutoff=3)
    print(f"\nOutgoing from A: {len(out_paths)} paths")
    for p in out_paths:
        print(f"  {format_path(p)}")
    
    # Test incoming
    in_paths = get_incoming_journey(G, "C", cutoff=3)
    print(f"\nIncoming to C: {len(in_paths)} paths")
    for p in in_paths:
        print(f"  {format_path(p)}")
    
    print("\nJourney module ready!")
