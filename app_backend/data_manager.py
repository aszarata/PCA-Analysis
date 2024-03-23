import pandas as pd
from sklearn.decomposition import PCA

from .pca_handler import PCAHandler


class DataManager:
    """
    Object responsible for data preprocessing and editing.
    """

    def __init__(self) -> None:
        self.input_df = None
        self.df = None

        # DataFrame in the last saved state
        self.df_last = None

    # Main Functions

    # Read from CSV file
    def read_from_csv(self, filename: str, sep: str = ';', header: int = 0) -> None:
        """
        Reads data from a CSV file.

        Args:
            filename (str): Name of the CSV file.
            sep (str, optional): Delimiter used in the CSV file. Defaults to ';'.
            header (int, optional): Row number to use as the column names. Defaults to 0.
        """
        self.input_df = pd.read_csv(filename, sep=sep, header=header)
        self.input_df.columns = self.input_df.columns.astype(str)
        self.df = self.input_df.copy()
        self.df_last = self.input_df.copy()

    # Get DataFrame
    def get_df(self) -> pd.DataFrame:
        """
        Returns the DataFrame.
        """
        return self.df

    # Reset to initial state
    def reset(self) -> None:
        """
        Resets DataFrame to the initial state.
        """
        self.df = self.input_df.copy()
        self.df_last = self.input_df.copy()

    # Undo to the last saved state
    def undo(self) -> None:
        """
        Reverts DataFrame to the last saved state.
        """
        self.df = self.df_last.copy()

    # Save the current state to df_last variable
    def save(self) -> None:
        """
        Saves the current state of DataFrame.
        """
        self.df_last = self.df.copy()

    # Variables

    # Delete a variable
    def delete_variable(self, name):
        """
        Deletes a variable from DataFrame.

        Args:
            name: Name of the variable to delete.
        """
        self.df.drop(columns=[name], inplace=True)

    # Rename a variable
    def rename_variable(self, old_name: str, new_name: str) -> None:
        """
        Renames a variable in the DataFrame.

        Args:
            old_name (str): Old name of the variable.
            new_name (str): New name of the variable.
        """
        self.df.rename(columns={old_name: new_name}, inplace=True)

    # Get the type of a variable
    def get_variable_type(self, name: str) -> str:
        """
        Gets the type of a variable.

        Args:
            name (str): Name of the variable.

        Returns:
            str: Type of the variable.
        """
        variable_type = self.df[name].dtype
        return self._translate_variable_type(variable_type)

    # Get types of variables
    def get_variable_types(self):
        """
        Gets types of all variables in DataFrame.

        Returns:
            pandas.Series: Series containing the data types of variables.
        """
        return self.df.dtypes

    # Standardize a variable
    def normalize_std(self, variable_name: str) -> None:
        """
        Performs standard normalization on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        mean_value = self.df[variable_name].mean()
        std_value = self.df[variable_name].std()
        self.df[variable_name] = (self.df[variable_name] - mean_value) / std_value
        # self.save() #aby zmiany sie od razu zapisaly

    # Normalize a variable based on quantiles
    def normalize_q(self, variable_name: str) -> None:
        """
        Performs quantile-based normalization on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        q25 = self.df[variable_name].quantile(0.25)
        q75 = self.df[variable_name].quantile(0.75)
        self.df[variable_name] = (self.df[variable_name] - q25) / (q75 - q25)

    # Standardize the entire dataset (all numerical features)
    def standarize_dataset(self) -> None:
        """
        Standardizes all numerical features in the DataFrame.
        """
        for variable in self.df.columns:
            if self.get_variable_type(variable) == 'numerical':
                self.normalize_std(variable)

    # One-Hot Encode a variable
    def one_hot_encode(self, variable_name: str) -> None:
        """
        Performs one-hot encoding on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        column = self.df[variable_name]
        encoded_df = pd.get_dummies(column, prefix=variable_name)

        # Encoding True and False to 0 and 1
        encoded_df = encoded_df.applymap(lambda x: 1 if x > 0 else 0)

        self.df.drop(columns=[variable_name], inplace=True)
        self.df = pd.concat([self.df, encoded_df], axis=1)

    # Helper Functions

    # Translate variable type name from pandas type
    def _translate_variable_type(self, variable_type: str) -> str:
        """
        Translates the variable type from pandas type.

        Args:
            variable_type (str): Type of the variable.

        Returns:
            str: Translated variable type.
        """
        if variable_type != 'object':
            return 'numerical'
        return 'categorical'

    # PCA

    # Function performing PCA analysis returning a separate PCAHandler object.
    def PCA(self, n_components: int) -> PCAHandler:
        """
        Performs PCA analysis and returns a PCAHandler object.

        Args:
            n_components (int): Number of principal components to keep.

        Returns:
            PCAHandler: PCAHandler object containing PCA results.
        """
        pca_data = PCA(n_components=n_components)
        principal_components = pca_data.fit_transform(self.df)  # PCA Analysis

        pca_df = pd.DataFrame(data=principal_components, columns=None)  # Prepare PCA object

        return PCAHandler(pca_df)
