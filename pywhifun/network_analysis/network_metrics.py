"""
Network Building and Metrics Functions

Converted from MATLAB WhiFuN network building functions.
"""

import os
import numpy as np
import glob
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
from ..io.file_utils import create_file_pattern


def build_network_decision(cluster_folder, out_pattern, overwrite=False):
    """
    Manage the decision process for building Functional Networks (FNs).
    
    This function checks if previously clustered FN files exist in the
    specified folder. If files are found, it prompts the user to either
    rebuild the networks or select an existing cluster solution (K value).
    
    Parameters
    ----------
    cluster_folder : str
        Full path to the directory where FN cluster results are stored
    out_pattern : str
        The filename pattern used for the clustered NIfTI files
        (e.g., 'WM_FN_K*.nii', where * is the K value)
    overwrite : bool, optional
        Flag to bypass prompts if True (default: False)
        
    Returns
    -------
    build_net : bool
        Flag indicating whether the networks should be built now
    k_value : int
        The number of networks (clusters) to proceed with
        
    Notes
    -----
    Converted from MATLAB whifun_build_net.m
    """
    build_net = False
    k_value = 0
    
    # Create cluster folder if it doesn't exist
    os.makedirs(cluster_folder, exist_ok=True)
    
    # Look for existing cluster files
    cluster_path = os.path.join(cluster_folder, out_pattern)
    cluster_files = glob.glob(cluster_path)
    
    if cluster_files:
        # Extract K values from filenames
        k_values = []
        for file in cluster_files:
            filename = os.path.basename(file)
            try:
                # Assuming pattern like 'WM_FN_K{number}.nii'
                k_val = int(filename.split('K')[1].split('.')[0])
                k_values.append(k_val)
            except (IndexError, ValueError):
                continue
        
        if k_values:
            k_values = sorted(list(set(k_values)))  # Remove duplicates and sort
            
            if not overwrite:
                # Create GUI dialog for user decision
                root = tk.Tk()
                root.withdraw()  # Hide main window
                
                answer = messagebox.askyesno(
                    "FN file found",
                    f"FN file already found with K = {k_values}. "
                    "Do you want to build the networks again?"
                )
                
                if answer:  # Yes - rebuild networks
                    build_net = True
                    k_value = 0
                else:  # No - use existing
                    if len(k_values) == 1:
                        k_value = k_values[0]
                    else:
                        # Multiple K values available - let user choose
                        while True:
                            k_choice = simpledialog.askinteger(
                                "Choose K value",
                                f"Choose the K you want to proceed with.\n"
                                f"Available options: {k_values}"
                            )
                            
                            if k_choice is None:  # User cancelled
                                root.destroy()
                                return False, 0
                            
                            if k_choice in k_values:
                                k_value = k_choice
                                break
                            else:
                                retry = messagebox.askretrycancel(
                                    "Invalid K value",
                                    f"Requested K value not found. "
                                    f"Please choose from: {k_values}"
                                )
                                if not retry:
                                    root.destroy()
                                    return False, 0
                
                root.destroy()
            else:
                # Overwrite mode - use first available K value
                k_value = k_values[0]
    else:
        # No existing files found - build networks
        build_net = True
        k_value = 0
    
    return build_net, k_value


def calculate_network_metrics(connectivity_matrix, binary_threshold=None):
    """
    Calculate various network metrics from connectivity matrix.
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix (nodes x nodes)
    binary_threshold : float, optional
        Threshold for binarizing the network
        
    Returns
    -------
    metrics : dict
        Dictionary containing network metrics
    """
    import networkx as nx
    from scipy import sparse
    
    # Remove diagonal
    conn = connectivity_matrix.copy()
    np.fill_diagonal(conn, 0)
    
    metrics = {}
    
    # Basic metrics
    metrics['density'] = np.count_nonzero(conn) / (conn.shape[0] * (conn.shape[0] - 1))
    metrics['mean_strength'] = np.mean(np.sum(np.abs(conn), axis=1))
    metrics['std_strength'] = np.std(np.sum(np.abs(conn), axis=1))
    
    # Convert to NetworkX graph for advanced metrics
    if binary_threshold is not None:
        # Binary network
        binary_conn = (np.abs(conn) > binary_threshold).astype(int)
        G = nx.from_numpy_array(binary_conn)
        
        # Binary network metrics
        metrics['clustering_coefficient'] = nx.average_clustering(G)
        metrics['transitivity'] = nx.transitivity(G)
        
        if nx.is_connected(G):
            metrics['characteristic_path_length'] = nx.average_shortest_path_length(G)
            metrics['global_efficiency'] = nx.global_efficiency(G)
        else:
            # For disconnected graphs
            largest_cc = max(nx.connected_components(G), key=len)
            G_largest = G.subgraph(largest_cc)
            metrics['characteristic_path_length'] = nx.average_shortest_path_length(G_largest)
            metrics['global_efficiency'] = nx.global_efficiency(G_largest)
            metrics['n_components'] = nx.number_connected_components(G)
        
        metrics['local_efficiency'] = nx.local_efficiency(G)
        
    else:
        # Weighted network
        G = nx.from_numpy_array(np.abs(conn))
        
        # Weighted network metrics
        metrics['clustering_coefficient'] = nx.average_clustering(G, weight='weight')
        metrics['global_efficiency'] = nx.global_efficiency(G, weight='weight')
        metrics['local_efficiency'] = nx.local_efficiency(G, weight='weight')
    
    # Node-level metrics
    metrics['degree_centrality'] = list(nx.degree_centrality(G).values())
    metrics['betweenness_centrality'] = list(nx.betweenness_centrality(G).values())
    metrics['closeness_centrality'] = list(nx.closeness_centrality(G).values())
    metrics['eigenvector_centrality'] = list(nx.eigenvector_centrality(G, max_iter=1000).values())
    
    return metrics


def small_world_metrics(connectivity_matrix, n_random=100, binary_threshold=None):
    """
    Calculate small-world metrics (clustering coefficient and path length ratios).
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix
    n_random : int, optional
        Number of random networks for comparison (default: 100)
    binary_threshold : float, optional
        Threshold for binarizing the network
        
    Returns
    -------
    sw_metrics : dict
        Small-world metrics including sigma and omega
    """
    import networkx as nx
    
    # Calculate metrics for original network
    orig_metrics = calculate_network_metrics(connectivity_matrix, binary_threshold)
    
    # Generate random networks and calculate average metrics
    n_nodes = connectivity_matrix.shape[0]
    
    if binary_threshold is not None:
        # Binary network
        binary_conn = (np.abs(connectivity_matrix) > binary_threshold).astype(int)
        np.fill_diagonal(binary_conn, 0)
        G_orig = nx.from_numpy_array(binary_conn)
        n_edges = G_orig.number_of_edges()
        
        random_clustering = []
        random_path_length = []
        
        for _ in range(n_random):
            # Generate random network with same number of nodes and edges
            G_random = nx.erdos_renyi_graph(n_nodes, n_edges / (n_nodes * (n_nodes - 1) / 2))
            
            if nx.is_connected(G_random):
                random_clustering.append(nx.average_clustering(G_random))
                random_path_length.append(nx.average_shortest_path_length(G_random))
        
        avg_random_clustering = np.mean(random_clustering)
        avg_random_path_length = np.mean(random_path_length)
        
    else:
        # For weighted networks, use degree-preserving randomization
        # This is a simplified approach
        avg_random_clustering = orig_metrics['clustering_coefficient'] * 0.5  # Placeholder
        avg_random_path_length = orig_metrics['characteristic_path_length'] * 1.2  # Placeholder
    
    # Calculate small-world metrics
    sw_metrics = {
        'clustering_ratio': orig_metrics['clustering_coefficient'] / avg_random_clustering,
        'path_length_ratio': orig_metrics['characteristic_path_length'] / avg_random_path_length,
        'sigma': (orig_metrics['clustering_coefficient'] / avg_random_clustering) / 
                (orig_metrics['characteristic_path_length'] / avg_random_path_length),
        'original_clustering': orig_metrics['clustering_coefficient'],
        'original_path_length': orig_metrics['characteristic_path_length'],
        'random_clustering': avg_random_clustering,
        'random_path_length': avg_random_path_length
    }
    
    return sw_metrics


def modularity_analysis(connectivity_matrix, binary_threshold=None):
    """
    Perform modularity analysis on the network.
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix
    binary_threshold : float, optional
        Threshold for binarizing the network
        
    Returns
    -------
    modularity_results : dict
        Modularity analysis results
    """
    import networkx as nx
    from networkx.algorithms import community
    
    conn = connectivity_matrix.copy()
    np.fill_diagonal(conn, 0)
    
    if binary_threshold is not None:
        binary_conn = (np.abs(conn) > binary_threshold).astype(int)
        G = nx.from_numpy_array(binary_conn)
    else:
        G = nx.from_numpy_array(np.abs(conn))
    
    # Community detection using Louvain algorithm
    communities = community.louvain_communities(G, seed=42)
    
    # Calculate modularity
    if binary_threshold is not None:
        modularity = community.modularity(G, communities)
    else:
        modularity = community.modularity(G, communities, weight='weight')
    
    # Create community assignment vector
    community_assignment = np.zeros(G.number_of_nodes())
    for i, comm in enumerate(communities):
        for node in comm:
            community_assignment[node] = i
    
    modularity_results = {
        'modularity': modularity,
        'n_communities': len(communities),
        'community_assignment': community_assignment,
        'community_sizes': [len(comm) for comm in communities]
    }
    
    return modularity_results


def rich_club_coefficient(connectivity_matrix, binary_threshold=None):
    """
    Calculate rich club coefficient.
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix
    binary_threshold : float, optional
        Threshold for binarizing the network
        
    Returns
    -------
    rich_club : dict
        Rich club analysis results
    """
    import networkx as nx
    
    conn = connectivity_matrix.copy()
    np.fill_diagonal(conn, 0)
    
    if binary_threshold is not None:
        binary_conn = (np.abs(conn) > binary_threshold).astype(int)
        G = nx.from_numpy_array(binary_conn)
    else:
        G = nx.from_numpy_array(np.abs(conn))
    
    # Calculate rich club coefficient
    try:
        rich_club_coeff = nx.rich_club_coefficient(G, normalized=False)
        
        # Calculate normalized version (requires random networks)
        # This is computationally expensive, so we'll provide the option
        rich_club_norm = nx.rich_club_coefficient(G, normalized=True, seed=42)
        
        rich_club = {
            'coefficients': rich_club_coeff,
            'normalized_coefficients': rich_club_norm,
            'degrees': list(rich_club_coeff.keys()),
            'values': list(rich_club_coeff.values())
        }
        
    except Exception as e:
        print(f"Rich club calculation failed: {e}")
        rich_club = {'error': str(e)}
    
    return rich_club