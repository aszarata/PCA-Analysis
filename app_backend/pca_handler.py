from itertools import combinations

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

    def __init__(self, data: pd.DataFrame) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame.")

        if len(data.columns) < 2:
            raise ValueError("Input DataFrame must have at least two columns.")

        self.df = data.copy()

        # Rename columns
        columns = [f'pc{i + 1}' for i in range(len(data.columns))]
        self.df.columns = columns

        # Labels after clustering
        self.labels = None

    def get_df(self) -> pd.DataFrame:
        return self.df

    # Two-dimensional plot
    def plot_2d(self, x_component: str, y_component: str, title: str = None) -> plt:
        """
        Generates a 2D scatter plot.
    
        Args:
            x_component (str): Name of the component for x-axis.
            y_component (str): Name of the component for y-axis.
            title (str, optional): Title of the plot. Defaults to None.
    
        Returns:
            plt: Matplotlib plot object.
        """
        if x_component not in self.df.columns or y_component not in self.df.columns:
            raise ValueError("Invalid component name. Make sure the specified components exist in the DataFrame.")

        plt.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)

        plt.xlabel(x_component)
        plt.ylabel(y_component)

        plt.title(title)

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

    # K-means clusters suggestion
    def suggest_clusters_kmeans(self, max_clusters: int = 10, draw_graph: bool = False) -> int:
        """
        Suggests the optimal number of clusters using the elbow method for K-means clustering.

        Args:
            max_clusters (int): Maximum number of clusters to consider.
            draw_graph (bool):  Draw plot of the second derivative for test purposes

        Returns:
            int: Optimal number of clusters.
        """
        if max_clusters <= 1:
            raise ValueError("Max clusters must be greater than 1.")

        distortions = []
        for i in range(1, max_clusters + 1):
            tmp_df = self.df.copy()
            kmeans = KMeans(n_clusters=i, n_init='auto')
            kmeans.fit(tmp_df)
            distortions.append(kmeans.inertia_)
        # Calculate the change in distortion between consecutive cluster numbers
        distortions_change = np.diff(distortions)
        # Calculate the second derivative (acceleration) of the distortion change
        acceleration = np.diff(distortions_change)
        # Find the "knee" point where acceleration starts to decrease
        knee_index = np.argmax(acceleration) + 2

        if draw_graph:
            plt.plot(range(1, len(acceleration) + 1), acceleration, marker='o')
            plt.xlabel('Number of clusters')
            plt.ylabel('Distortion')
            plt.title('Elbow Method for Optimal k - Second derivative')
            plt.show()
        return knee_index

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

    # DBSCAN cluster suggestion
    def suggest_clusters_dbscan(self, min_samples: int, draw_graph: bool = False) -> float:
        """
        Suggests the optimal value of epsilon (eps) for DBSCAN clustering using k-distance graph.

        Args:
            min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.
            draw_graph (bool): Draw plot of the second derivative for test purposes

        Returns:
            float: Optimal value of epsilon.
        """
        if min_samples <= 0:
            raise ValueError("Minimum number of samples must be greater than zero.")

        # Calculate pairwise distances between points
        distance_matrix = pairwise_distances(self.df)
        max_distance = np.max(distance_matrix)

        # Choose range of epsilon values as percentage of max distance
        eps_values = np.linspace(0.1 * max_distance, 0.9 * max_distance, 5)

        distances = []
        for eps in eps_values:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            dbscan.fit(self.df)
            # Calculate pairwise distances between points
            distance_matrix = pairwise_distances(self.df)
            # Sort and flatten distance matrix
            sorted_distances = np.sort(distance_matrix.flatten())
            distances.append(sorted_distances[min_samples])

        # Find the "knee" in the graph (optimal epsilon)
        knee_index = np.argmax(np.gradient(distances))

        if draw_graph:
            plt.plot(eps_values, distances, marker='o')
            plt.xlabel('Epsilon (distance)')
            plt.ylabel('Minimum Distance')
            plt.title('K-Distance Graph for Optimal eps')
            plt.show()

            # Plot the second derivative for test purposes
            plt.plot(eps_values, np.gradient(distances))
            plt.xlabel('Epsilon (distance)')
            plt.ylabel('Second Derivative')
            plt.title('Second Derivative of Distance')
            plt.show()

        return eps_values[knee_index]
