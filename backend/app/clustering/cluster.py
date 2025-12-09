"""K-means clustering for music features."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Optional


FEATURE_COLUMNS = [
    'bpm_normalized',
    'energy',
    'danceability',
    'acousticness',
    'valence',
    'instrumentalness',
    'loudness'
]


def train_clusters(features_df: pd.DataFrame, n_clusters: int = 8) -> tuple[KMeans, float]:
    """
    Train k-means clustering model on song features.

    Args:
        features_df: DataFrame with feature columns
        n_clusters: Number of clusters to create

    Returns:
        Tuple of (trained KMeans model, silhouette score)
    """
    X = features_df[FEATURE_COLUMNS].values

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(X)

    score = silhouette_score(X, model.labels_)
    return model, score


def find_optimal_k(features_df: pd.DataFrame, k_range: range = range(4, 15)) -> int:
    """
    Find optimal number of clusters using silhouette score.

    Args:
        features_df: DataFrame with feature columns
        k_range: Range of k values to try

    Returns:
        Optimal number of clusters
    """
    X = features_df[FEATURE_COLUMNS].values

    best_k = k_range.start
    best_score = -1

    for k in k_range:
        if k >= len(X):
            break

        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        score = silhouette_score(X, labels)

        if score > best_score:
            best_score = score
            best_k = k

    return best_k


def assign_clusters(model: KMeans, features_df: pd.DataFrame) -> pd.Series:
    """
    Assign cluster labels to songs.

    Args:
        model: Trained KMeans model
        features_df: DataFrame with feature columns

    Returns:
        Series of cluster labels
    """
    X = features_df[FEATURE_COLUMNS].values
    return pd.Series(model.predict(X), index=features_df.index)


def get_cluster_centroids(model: KMeans) -> list[dict]:
    """
    Get cluster centroids as list of feature dictionaries.

    Args:
        model: Trained KMeans model

    Returns:
        List of centroid dictionaries
    """
    centroids = []
    for i, centroid in enumerate(model.cluster_centers_):
        centroid_dict = {
            "cluster_id": i,
            **{FEATURE_COLUMNS[j]: float(centroid[j]) for j in range(len(FEATURE_COLUMNS))}
        }
        centroids.append(centroid_dict)
    return centroids


def reduce_for_visualization(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce features to 2D using PCA for visualization.

    Args:
        features_df: DataFrame with feature columns

    Returns:
        DataFrame with x, y coordinates
    """
    X = features_df[FEATURE_COLUMNS].values

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)

    return pd.DataFrame({
        'x': coords[:, 0],
        'y': coords[:, 1]
    }, index=features_df.index)


def reduce_centroids_for_visualization(
    centroids: list[dict],
    features_df: pd.DataFrame
) -> list[dict]:
    """
    Project centroids to same 2D PCA space as songs.

    Args:
        centroids: List of centroid dictionaries
        features_df: DataFrame used for fitting PCA

    Returns:
        List of centroids with x, y coordinates
    """
    # Fit PCA on song features
    X = features_df[FEATURE_COLUMNS].values
    pca = PCA(n_components=2, random_state=42)
    pca.fit(X)

    # Transform centroids
    centroid_array = np.array([
        [c[col] for col in FEATURE_COLUMNS]
        for c in centroids
    ])
    coords = pca.transform(centroid_array)

    result = []
    for i, centroid in enumerate(centroids):
        result.append({
            "cluster_id": centroid["cluster_id"],
            "x": float(coords[i, 0]),
            "y": float(coords[i, 1])
        })
    return result
