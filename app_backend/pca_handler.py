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

    def plot_2d(self, x_component: str, y_component: str, title: str = None, ax=None):
        """
        Generates a 2D scatter plot on the given axes.

        Args:
            x_component (str): Name of the component for x-axis.
            y_component (str): Name of the component for y-axis.
            title (str, optional): Title of the plot. Defaults to None.
            ax (matplotlib.axes.Axes, optional): Axes object on which to draw the plot. Defaults to None.

        Returns:
            matplotlib.axes.Axes: The axes object with the plot.
        """
        if ax is None:
            fig, ax = plt.subplots()  # Create a new figure and axes if not provided

        scatter = ax.scatter(self.df[x_component], self.df[y_component], alpha=0.5, c=self.labels)

        ax.set_xlabel(x_component)
        ax.set_ylabel(y_component)
        ax.set_title(title)

        # Optionally, if you have labels for the colors, you can add a legend:
        # legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
        # ax.add_artist(legend1)

        return ax

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
