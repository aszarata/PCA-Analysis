from itertools import combinations

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN

class PCAHandler:
    """
    Object responsible for handling data returned by PCA analysis from 
    DataManager, including clustering and generating plots.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self.df = data

        # Rename columns
        columns = [f'pc{i + 1}' for i in range(len(data.columns))]
        self.df.columns = columns

        # Labels after clustering
        self.labels = None

    def get_df(self) -> pd.DataFrame:
        return self.df

    # Two-dimensional plot
    # def plot_2d(self, x_component: str, y_component: str, title: str = None) -> plt:
    #     """
    #     Generates a 2D scatter plot.
    #
    #     Args:
    #         x_component (str): Name of the component for x-axis.
    #         y_component (str): Name of the component for y-axis.
    #         title (str, optional): Title of the plot. Defaults to None.
    #
    #     Returns:
    #         plt: Matplotlib plot object.
    #     """
    #
    #     plt.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)
    #
    #     plt.xlabel(x_component)
    #     plt.ylabel(y_component)
    #
    #     plt.title(title)
    #
    #     return plt

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

    def plot_2d(self, x_component: str, y_component: str, title: str = None, ax=None):
        """
        Generates a 2D scatter plot on the given axes.

        Args:
            x_component (str): Name of the component for x-axis.
            y_component (str): Name of the component for y-axis.
            title (str, optional): Title of the plot. If None, the title will be automatically generated based on the PCA components. Defaults to None.
            ax (matplotlib.axes.Axes, optional): Axes object on which to draw the plot. Defaults to None.

        Returns:
            matplotlib.axes.Axes: The axes object with the plot.
        """
        if ax is None:
            fig, ax = plt.subplots()  # Create a new figure and axes if not provided

        scatter = ax.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)

        ax.set_xlabel(x_component)
        ax.set_ylabel(y_component)

        # Automatically generate title if not provided
        if title is None:
            num_components = len(self.df.columns)
            title = f'PCA Analysis: Plot of {x_component} vs {y_component} - {num_components} Components'
        ax.set_title(title)

        # Optionally, if you have labels for the colors, you can add a legend:
        # legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
        # ax.add_artist(legend1)

        return ax

    # extra method
    def plot_all_2d_combinations(self, components: list, title_prefix: str = 'PCA Analysis'):
        """
        Generates 2D scatter plots for all combinations of the specified components.

        Args:
            components (list): List of component names (strings) to be combined and plotted.
            title_prefix (str): Prefix for the plot title.
        """
        fig, axes = plt.subplots(nrows=len(components), ncols=len(components) // 2, figsize=(15, 10))
        axes = axes.flatten()  # Flatten in case of single row/column to simplify indexing

        for i, (x_component, y_component) in enumerate(combinations(components, 2)):
            self.plot_2d(x_component, y_component, title=f'{title_prefix}: {x_component} vs {y_component}', ax=axes[i])

        plt.tight_layout()
        plt.show()

    # K-means clustering
    def kmeans_clustering(self, num_clusters: int) -> None:
        """
        Performs K-means clustering on the data.

        Args:
            num_clusters (int): Number of clusters to form.
        """
        kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
        kmeans.fit(self.df)
        self.labels = kmeans.labels_

    # DBSCAN clustering
    def dbscan_clustering(self, eps: float, min_samples: int) -> None:
        """
        Performs DBSCAN clustering on the data.

        Args:
            eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
            min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.
        """
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.labels = dbscan.fit_predict(self.df)
