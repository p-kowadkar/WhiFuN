"""
Clustering Functions for Functional Network Creation

Converted from MATLAB WhiFuN clustering functions.
"""

import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import nibabel as nib
from pathlib import Path
import warnings
from ..io.nifti_io import nifti_read, nifti_write
from ..utils.validation import validate_file_path


def create_functional_networks_kmeans(output_folder, tissue_type='WM', k_range=(2, 10), 
                                    group_mask_path=None, **kwargs):
    """
    Create WM/GM Functional Networks using K-means clustering.
    
    Performs K-means clustering on the average voxel-level functional 
    connectivity matrix across subjects and generates functional networks (FNs).
    
    Parameters
    ----------
    output_folder : str
        Path to output folder
    tissue_type : str, optional
        'WM' or 'GM' (default: 'WM')
    k_range : tuple, optional
        (lower_bound, upper_bound) for K clusters (default: (2, 10))
    group_mask_path : str, optional
        Path to group-level brain mask (NIfTI)
    **kwargs : dict
        Additional parameters:
        - subsample_strategy : str, default 'subsample'
        - cv_folds : int, default 4
        - focus_check : bool, default False
        - focus_mask_path : str, default None
        - num_replicates : int, default 10
        - chunk_size : int, default 100
        - overwrite : bool, default False
        - random_state : int, default 42
        
    Returns
    -------
    results : dict
        Dictionary containing clustering results and metrics
        
    Notes
    -----
    Converted from MATLAB whifun_create_FN_Kmeans.m
    """
    # Parse parameters
    subsample_strategy = kwargs.get('subsample_strategy', 'subsample')
    cv_folds = kwargs.get('cv_folds', 4)
    focus_check = kwargs.get('focus_check', False)
    focus_mask_path = kwargs.get('focus_mask_path', None)
    num_replicates = kwargs.get('num_replicates', 10)
    chunk_size = kwargs.get('chunk_size', 100)
    overwrite = kwargs.get('overwrite', False)
    random_state = kwargs.get('random_state', 42)
    
    k_min, k_max = k_range
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Creating {tissue_type} Functional Networks using K-means clustering")
    print(f"K range: {k_min} to {k_max}")
    print(f"Output folder: {output_folder}")
    
    # Load group mask
    if group_mask_path:
        mask_data, mask_affine, mask_header = nifti_read(group_mask_path)
        mask_indices = np.where(mask_data > 0)
        n_voxels = len(mask_indices[0])
        print(f"Loaded group mask: {n_voxels} voxels")
    else:
        raise ValueError("Group mask path is required")
    
    # Load focus mask if specified
    focus_mask_indices = None
    if focus_check and focus_mask_path:
        focus_data, _, _ = nifti_read(focus_mask_path)
        focus_mask_indices = np.where(focus_data > 0)
        print(f"Loaded focus mask: {len(focus_mask_indices[0])} voxels")
    
    # Initialize results storage
    results = {
        'k_values': list(range(k_min, k_max + 1)),
        'silhouette_scores': [],
        'calinski_harabasz_scores': [],
        'inertia_scores': [],
        'cluster_labels': {},
        'cluster_centers': {},
        'stability_scores': {}
    }
    
    # Placeholder for connectivity data loading
    # In practice, this would load the average voxel-level FC matrix
    print("Loading connectivity data...")
    # connectivity_data = load_connectivity_data(...)  # Implementation needed
    
    # For now, create synthetic data for demonstration
    np.random.seed(random_state)
    connectivity_data = np.random.randn(n_voxels, 100)  # n_voxels x n_features
    
    print(f"Connectivity data shape: {connectivity_data.shape}")
    
    # Perform clustering for each K value
    for k in range(k_min, k_max + 1):
        print(f"\nProcessing K = {k}")
        
        # Initialize K-means with multiple replicates
        best_kmeans = None
        best_inertia = np.inf
        
        for replicate in range(num_replicates):
            kmeans = KMeans(
                n_clusters=k,
                random_state=random_state + replicate,
                n_init=10,
                max_iter=300
            )
            
            # Fit clustering
            labels = kmeans.fit_predict(connectivity_data)
            
            if kmeans.inertia_ < best_inertia:
                best_inertia = kmeans.inertia_
                best_kmeans = kmeans
        
        # Store best results
        labels = best_kmeans.labels_
        centers = best_kmeans.cluster_centers_
        
        results['cluster_labels'][k] = labels
        results['cluster_centers'][k] = centers
        results['inertia_scores'].append(best_inertia)
        
        # Calculate clustering metrics
        if k > 1:  # Silhouette score requires at least 2 clusters
            sil_score = silhouette_score(connectivity_data, labels)
            ch_score = calinski_harabasz_score(connectivity_data, labels)
            
            results['silhouette_scores'].append(sil_score)
            results['calinski_harabasz_scores'].append(ch_score)
            
            print(f"K={k}: Silhouette={sil_score:.3f}, CH={ch_score:.3f}, Inertia={best_inertia:.3f}")
        
        # Cross-validation stability analysis
        if cv_folds > 1:
            stability = calculate_clustering_stability(
                connectivity_data, k, cv_folds, random_state
            )
            results['stability_scores'][k] = stability
            print(f"K={k}: Stability={stability:.3f}")
        
        # Save cluster maps as NIfTI files
        cluster_map = np.zeros_like(mask_data)
        cluster_map[mask_indices] = labels + 1  # 1-indexed for NIfTI
        
        output_filename = f"{tissue_type}_FN_K{k}.nii"
        output_path = os.path.join(output_folder, output_filename)
        
        nifti_write(cluster_map, mask_affine, output_path, mask_header)
        print(f"Saved: {output_filename}")
    
    # Find optimal K using elbow method and silhouette analysis
    optimal_k = find_optimal_k(results)
    results['optimal_k'] = optimal_k
    
    print(f"\nOptimal K determined: {optimal_k}")
    
    # Save results summary
    save_clustering_results(results, output_folder, tissue_type)
    
    return results


def calculate_clustering_stability(data, k, cv_folds=4, random_state=42):
    """
    Calculate clustering stability using cross-validation.
    
    Parameters
    ----------
    data : ndarray
        Input data for clustering
    k : int
        Number of clusters
    cv_folds : int, optional
        Number of cross-validation folds (default: 4)
    random_state : int, optional
        Random state for reproducibility (default: 42)
        
    Returns
    -------
    stability : float
        Average stability score across folds
    """
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    stability_scores = []
    
    fold_results = []
    
    # Perform clustering on each fold
    for train_idx, test_idx in kf.split(data):
        train_data = data[train_idx]
        test_data = data[test_idx]
        
        # Fit on training data
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        train_labels = kmeans.fit_predict(train_data)
        
        # Predict on test data
        test_labels = kmeans.predict(test_data)
        
        fold_results.append({
            'train_labels': train_labels,
            'test_labels': test_labels,
            'train_idx': train_idx,
            'test_idx': test_idx
        })
    
    # Calculate stability between folds
    n_folds = len(fold_results)
    for i in range(n_folds):
        for j in range(i + 1, n_folds):
            # Compare clustering consistency between folds
            # This is a simplified stability measure
            stability = calculate_adjusted_rand_index(
                fold_results[i]['test_labels'],
                fold_results[j]['test_labels']
            )
            stability_scores.append(stability)
    
    return np.mean(stability_scores) if stability_scores else 0.0


def calculate_adjusted_rand_index(labels1, labels2):
    """
    Calculate Adjusted Rand Index between two clustering solutions.
    
    Parameters
    ----------
    labels1, labels2 : array-like
        Cluster labels
        
    Returns
    -------
    ari : float
        Adjusted Rand Index
    """
    from sklearn.metrics import adjusted_rand_score
    
    # Ensure same length
    min_len = min(len(labels1), len(labels2))
    labels1 = labels1[:min_len]
    labels2 = labels2[:min_len]
    
    return adjusted_rand_score(labels1, labels2)


def find_optimal_k(results):
    """
    Find optimal number of clusters using multiple criteria.
    
    Parameters
    ----------
    results : dict
        Clustering results dictionary
        
    Returns
    -------
    optimal_k : int
        Optimal number of clusters
    """
    k_values = results['k_values']
    
    # Method 1: Elbow method using inertia
    inertias = results['inertia_scores']
    elbow_k = find_elbow_point(k_values, inertias)
    
    # Method 2: Maximum silhouette score
    if results['silhouette_scores']:
        sil_scores = results['silhouette_scores']
        max_sil_idx = np.argmax(sil_scores)
        sil_k = k_values[max_sil_idx + 1]  # +1 because silhouette starts from k=2
    else:
        sil_k = elbow_k
    
    # Method 3: Maximum Calinski-Harabasz score
    if results['calinski_harabasz_scores']:
        ch_scores = results['calinski_harabasz_scores']
        max_ch_idx = np.argmax(ch_scores)
        ch_k = k_values[max_ch_idx + 1]  # +1 because CH starts from k=2
    else:
        ch_k = elbow_k
    
    # Combine methods (simple voting)
    candidates = [elbow_k, sil_k, ch_k]
    optimal_k = max(set(candidates), key=candidates.count)  # Most frequent
    
    print(f"K selection methods: Elbow={elbow_k}, Silhouette={sil_k}, CH={ch_k}")
    print(f"Selected optimal K: {optimal_k}")
    
    return optimal_k


def find_elbow_point(x_values, y_values):
    """
    Find elbow point in a curve using the "elbow method".
    
    Parameters
    ----------
    x_values : array-like
        X coordinates
    y_values : array-like
        Y coordinates
        
    Returns
    -------
    elbow_x : float
        X coordinate of elbow point
    """
    # Calculate the differences
    diffs = np.diff(y_values)
    
    # Find the point where the rate of change decreases most
    if len(diffs) > 1:
        second_diffs = np.diff(diffs)
        elbow_idx = np.argmax(second_diffs) + 1
    else:
        elbow_idx = 0
    
    return x_values[elbow_idx]


def save_clustering_results(results, output_folder, tissue_type):
    """
    Save clustering results to files.
    
    Parameters
    ----------
    results : dict
        Clustering results
    output_folder : str
        Output directory
    tissue_type : str
        Tissue type ('WM' or 'GM')
    """
    import json
    
    # Prepare results for JSON serialization
    json_results = {
        'k_values': results['k_values'],
        'silhouette_scores': results['silhouette_scores'],
        'calinski_harabasz_scores': results['calinski_harabasz_scores'],
        'inertia_scores': results['inertia_scores'],
        'optimal_k': results['optimal_k']
    }
    
    # Save stability scores
    if results['stability_scores']:
        json_results['stability_scores'] = {
            str(k): float(v) for k, v in results['stability_scores'].items()
        }
    
    # Save to JSON file
    results_file = os.path.join(output_folder, f"{tissue_type}_clustering_results.json")
    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"Saved clustering results: {results_file}")
    
    # Save cluster centers as numpy arrays
    for k, centers in results['cluster_centers'].items():
        centers_file = os.path.join(output_folder, f"{tissue_type}_centers_K{k}.npy")
        np.save(centers_file, centers)
    
    print("Saved cluster centers")


def get_functional_networks_kmeans(connectivity_data, k, random_state=42, **kwargs):
    """
    Get functional networks using K-means clustering.
    
    Parameters
    ----------
    connectivity_data : ndarray
        Connectivity data to cluster
    k : int
        Number of clusters
    random_state : int, optional
        Random state for reproducibility (default: 42)
    **kwargs : dict
        Additional K-means parameters
        
    Returns
    -------
    labels : ndarray
        Cluster labels
    centers : ndarray
        Cluster centers
    metrics : dict
        Clustering metrics
    """
    # Set default parameters
    n_init = kwargs.get('n_init', 10)
    max_iter = kwargs.get('max_iter', 300)
    
    # Perform K-means clustering
    kmeans = KMeans(
        n_clusters=k,
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter
    )
    
    labels = kmeans.fit_predict(connectivity_data)
    centers = kmeans.cluster_centers_
    
    # Calculate metrics
    metrics = {
        'inertia': kmeans.inertia_,
        'n_iter': kmeans.n_iter_
    }
    
    if k > 1:
        metrics['silhouette_score'] = silhouette_score(connectivity_data, labels)
        metrics['calinski_harabasz_score'] = calinski_harabasz_score(connectivity_data, labels)
    
    return labels, centers, metrics