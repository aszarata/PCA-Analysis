from itertools import combinations
from sklearn.metrics import silhouette_score

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import pairwise_distances


class PCAHandler:
    """
    Object responsible for handling data returned by PCA analysis from 
    DataManager, including clustering and generating plots.
    """

    def __init__(self, data: pd.DataFrame, explained_variance) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame.")

        if len(data.columns) < 2:
            raise ValueError("Input DataFrame must have at least two columns.")

        self.df = data.copy()
        self.explained_variance = explained_variance

        # Rename columns
        columns = [f'pc{i + 1}' for i in range(len(data.columns))]
        self.df.columns = columns

        # Labels after clustering
        self.labels = None
        self.group_features = None

    def get_df(self) -> pd.DataFrame:
        return self.df

    def plot_2d(self, x_component: str, y_component: str, title: str = None) -> plt:
        """
        Generates a 2D scatter plot.

        Args:
            x_component (str): Name of the component for x-axis.
            y_component (str): Name of the component for y-axis.
            title (str, optional): Title of the plot. Defaults to None.
            group_features (dict, optional): Dictionary containing feature names for each group. Defaults to None.

        Returns:
            plt: Matplotlib plot object.
        """
        plt.figure(figsize=(10,8))

        if x_component not in self.df.columns or y_component not in self.df.columns:
            raise ValueError("Invalid component name. Make sure the specified components exist in the DataFrame.")

        scatter = plt.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)

        plt.xlabel(x_component)
        plt.ylabel(y_component)

        plt.title(title)

        if self.labels is not None:
            handles, _ = scatter.legend_elements()
            labels = [f'Cluster {i}\nKey features: {", ".join(self.group_features[i])}' for i in self.group_features.keys()]
            plt.legend(handles, labels, loc='upper right')

        pca_info = "PCA Components:\n"
        pca_info += f"{x_component}: {self.explained_variance[0]:.2f}\n"
        pca_info += f"{y_component}: {self.explained_variance[1]:.2f}\n"
        
        plt.text(0.05, 0.95, pca_info, transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        return plt

    
    # Explained variance plot
    def plot_explained_variance(self, cumulative: bool=True):
        """
        Plot explained variance ratio.

        Args:
            cumulative (bool): True: Shows the graph of Cumulative Explained Variance. False: Shows just the graph of Explained Variance. Defaults to True.

        Returns:
            plt: Matplotlib plot object.
        """
        num_components = len(self.explained_variance)
        plt.figure(figsize=(8, 6))
        if cumulative:
            plt.plot(np.cumsum(self.explained_variance), marker='o') 
            plt.title('Cumulative Explained Variance Ratio for Principal Components')
        else:
            plt.plot(self.explained_variance, marker='o') 
            plt.title('Explained Variance Ratio for Principal Components')
        plt.xlabel('Principal Component')
        plt.ylabel('Explained Variance Ratio')
        
        
        return plt

    # def plot_2d(self, x_component: str, y_component: str, title: str = None, ax=None):
    #     """
    #     Generates a 2D scatter plot on the given axes.
    #
    #     Args:
    #         x_component (str): Name of the component for x-axis.
    #         y_component (str): Name of the component for y-axis.
    #         title (str, optional): Title of the plot. Defaults to None.
    #         ax (matplotlib.axes.Axes, optional): Axes object on which to draw the plot. Defaults to None.
    #
    #     Returns:
    #         matplotlib.axes.Axes: The axes object with the plot.
    #     """
    #     if ax is None:
    #         fig, ax = plt.subplots()  # Create a new figure and axes if not provided
    #
    #     scatter = ax.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)
    #
    #     ax.set_xlabel(x_component)
    #     ax.set_ylabel(y_component)
    #     ax.set_title(title)
    #
    #     # Optionally, if you have labels for the colors, you can add a legend:
    #     # legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
    #     # ax.add_artist(legend1)
    #
    #     return ax

    # def plot_2d(self, x_component: str, y_component: str, title: str = None, ax=None):
    #     """
    #     Generates a 2D scatter plot on the given axes.

    #     Args:
    #         x_component (str): Name of the component for x-axis.
    #         y_component (str): Name of the component for y-axis.
    #         title (str, optional): Title of the plot. If None, the title will be automatically generated based on the PCA components. Defaults to None.
    #         ax (matplotlib.axes.Axes, optional): Axes object on which to draw the plot. Defaults to None.

    #     Returns:
    #         matplotlib.axes.Axes: The axes object with the plot.
    #     """
    #     if ax is None:
    #         fig, ax = plt.subplots()  # Create a new figure and axes if not provided

    #     scatter = ax.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)

    #     ax.set_xlabel(x_component)
    #     ax.set_ylabel(y_component)

    #     # Automatically generate title if not provided
    #     if title is None:
    #         num_components = len(self.df.columns)
    #         title = f'PCA Analysis: Plot of {x_component} vs {y_component} - {num_components} Components'
    #     ax.set_title(title)

    #     # Optionally, if you have labels for the colors, you can add a legend:
    #     # legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
    #     # ax.add_artist(legend1)

    #     return ax

    # extra method
    # def plot_all_2d_combinations(self, components: list, title_prefix: str = 'PCA Analysis'):
    #     """
    #     Generates 2D scatter plots for all combinations of the specified components.

    #     Args:
    #         components (list): List of component names (strings) to be combined and plotted.
    #         title_prefix (str): Prefix for the plot title.
    #     """
    #     fig, axes = plt.subplots(nrows=len(components), ncols=len(components) // 2, figsize=(15, 10))
    #     axes = axes.flatten()  # Flatten in case of single row/column to simplify indexing

    #     for i, (x_component, y_component) in enumerate(combinations(components, 2)):
    #         self.plot_2d(x_component, y_component, title=f'{title_prefix}: {x_component} vs {y_component}', ax=axes[i])

    #     plt.tight_layout()
    #     plt.show()

    # K-means clustering
    def kmeans_clustering(self, num_clusters: int) -> None:
        """
        Performs K-means clustering on the data.

        Args:
            num_clusters (int): Number of clusters to form.
        """
        if num_clusters <= 0:
            raise ValueError("Number of clusters must be greater than zero.")

        kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
        self.labels = kmeans.fit_predict(self.df)

        cluster_centers = kmeans.cluster_centers_

        feature_names = self.df.columns
        self.group_features = {}

        for i, center in enumerate(cluster_centers):
            group_features_indices = center.argsort()[-3:][::-1]  # top 3 features for each group
            self.group_features[i] = [feature_names[idx] for idx in group_features_indices]


    # DBSCAN clustering
    def dbscan_clustering(self, eps: float, min_samples: int) -> None:
        """
        Performs DBSCAN clustering on the data.

        Args:
            eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
            min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.
        """
        if eps <= 0:
            raise ValueError("Epsilon (eps) must be greater than zero.")
        if min_samples <= 0:
            raise ValueError("Minimum number of samples must be greater than zero.")

        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.labels = dbscan.fit_predict(self.df)

        unique_labels = np.unique(self.labels)
        self.group_features = {}

        for label in unique_labels:
            if label == -1:
                continue  # ignore noise points
            group_indices = np.where(self.labels == label)[0]
            group_data = self.df.iloc[group_indices]
            group_center = np.mean(group_data, axis=0)
            group_features_indices = group_center.argsort()[-3:][::-1]  # top 3 features for each group
            self.group_features[label] = list(self.df.columns[group_features_indices])




    def suggest_clusters_kmeans(self, max_clusters: int = 10, draw_graph: bool = False) -> int:
        """
        Suggests the optimal number of clusters using silhouette score for K-means clustering.

        Args:
            max_clusters (int): Maximum number of clusters to consider.
            draw_graph (bool):  Draw plot of silhouette scores for test purposes.

        Returns:
            int: Optimal number of clusters.
        """
        if max_clusters <= 1:
            raise ValueError("Max clusters must be greater than 1.")

        silhouette_scores = []
        for i in range(2, max_clusters + 1):  # Start from 2 clusters for silhouette score
            kmeans = KMeans(n_clusters=i, n_init='auto')
            cluster_labels = kmeans.fit_predict(self.df)
            silhouette_avg = silhouette_score(self.df, cluster_labels)
            silhouette_scores.append(silhouette_avg)

        optimal_cluster_index = np.argmax(silhouette_scores) + 2

        if draw_graph:
            plt.plot(range(2, max_clusters + 1), silhouette_scores, marker='o')
            plt.xlabel('Number of clusters')
            plt.ylabel('Silhouette Score')
            plt.title('Silhouette Score for Optimal k')
            plt.show()

        return optimal_cluster_index


    # DBSCAN cluster suggestion using silhouette score
    def suggest_clusters_dbscan(self, min_samples: int, draw_graph: bool = False) -> float:
        """
        Suggests the optimal value of epsilon (eps) for DBSCAN clustering using silhouette score.

        Args:
            min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.
            draw_graph (bool): Draw plot of silhouette scores for test purposes.

        Returns:
            float: Optimal value of epsilon.
        """
        if min_samples <= 0:
            raise ValueError("Minimum number of samples must be greater than zero.")

        silhouette_scores = []
        # Choose range of epsilon values as percentage of max distance
        distance_matrix = pairwise_distances(self.df)
        max_distance = np.max(distance_matrix)
        eps_values = np.linspace(0.1 * max_distance, 0.9 * max_distance, 5)

        for eps in eps_values:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = dbscan.fit_predict(self.df)
            if len(np.unique(cluster_labels)) > 1:
                silhouette_avg = silhouette_score(self.df, cluster_labels)
                silhouette_scores.append(silhouette_avg)
            else:
                silhouette_scores.append(-1)

        optimal_eps_index = np.argmax(silhouette_scores)

        if draw_graph:
            plt.plot(eps_values, silhouette_scores, marker='o')
            plt.xlabel('Epsilon (distance)')
            plt.ylabel('Silhouette Score')
            plt.title('Silhouette Score for Optimal eps')
            plt.show()

        return eps_values[optimal_eps_index]
