"""
Basic plotting functions for PyWhiFuN

This module contains basic plotting functions for connectivity matrices,
network graphs, and brain montages.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, Any
import networkx as nx


def plot_connectivity_matrix(matrix: np.ndarray, 
                           labels: Optional[list] = None,
                           title: str = "Connectivity Matrix",
                           cmap: str = "RdBu_r",
                           figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Plot a connectivity matrix as a heatmap.
    
    Parameters
    ----------
    matrix : np.ndarray
        Connectivity matrix to plot
    labels : list, optional
        Labels for matrix rows/columns
    title : str
        Plot title
    cmap : str
        Colormap name
    figsize : tuple
        Figure size (width, height)
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap
    im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    
    # Add colorbar
    plt.colorbar(im, ax=ax)
    
    # Set labels if provided
    if labels is not None:
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)
    
    ax.set_title(title)
    plt.tight_layout()
    
    return fig


def plot_network_graph(adjacency_matrix: np.ndarray,
                      node_labels: Optional[list] = None,
                      threshold: float = 0.0,
                      layout: str = 'spring',
                      figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Plot a network graph from an adjacency matrix.
    
    Parameters
    ----------
    adjacency_matrix : np.ndarray
        Adjacency matrix representing the network
    node_labels : list, optional
        Labels for network nodes
    threshold : float
        Threshold for edge weights (edges below threshold are removed)
    layout : str
        Network layout algorithm ('spring', 'circular', 'random')
    figsize : tuple
        Figure size (width, height)
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create networkx graph
    G = nx.from_numpy_array(adjacency_matrix)
    
    # Remove edges below threshold
    if threshold > 0:
        edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) 
                          if abs(d['weight']) < threshold]
        G.remove_edges_from(edges_to_remove)
    
    # Choose layout
    if layout == 'spring':
        pos = nx.spring_layout(G)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    elif layout == 'random':
        pos = nx.random_layout(G)
    else:
        pos = nx.spring_layout(G)
    
    # Draw network
    nx.draw(G, pos, ax=ax, with_labels=True, 
            labels=dict(enumerate(node_labels)) if node_labels else None,
            node_color='lightblue', node_size=500, 
            font_size=8, font_weight='bold')
    
    ax.set_title("Network Graph")
    
    return fig


def create_montage(images: list, 
                  titles: Optional[list] = None,
                  ncols: int = 3,
                  figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
    """
    Create a montage of multiple images.
    
    Parameters
    ----------
    images : list
        List of 2D arrays representing images
    titles : list, optional
        Titles for each image
    ncols : int
        Number of columns in the montage
    figsize : tuple, optional
        Figure size (width, height)
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    n_images = len(images)
    nrows = int(np.ceil(n_images / ncols))
    
    if figsize is None:
        figsize = (ncols * 4, nrows * 3)
    
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    # Handle single row/column cases
    if nrows == 1 and ncols == 1:
        axes = [axes]
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i, img in enumerate(images):
        ax = axes[i]
        ax.imshow(img, cmap='gray')
        ax.axis('off')
        
        if titles and i < len(titles):
            ax.set_title(titles[i])
    
    # Hide unused subplots
    for i in range(n_images, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    
    return fig