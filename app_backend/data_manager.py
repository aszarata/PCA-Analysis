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
        self.last_file_path = None  # Dodanie atrybutu do przechowywania ścieżki do ostatniego pliku

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
        try:
            self.last_file_path = filename  # Aktualizacja ścieżki do ostatnio wczytanego pliku
            self.input_df = pd.read_csv(filename, sep=sep, header=header)
            self.input_df.columns = self.input_df.columns.astype(str)
            self.df = self.input_df.copy()
            self.df_last = self.input_df.copy()
        except FileNotFoundError:
            raise FileNotFoundError("Specified file not found.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the file: {str(e)}")

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

    # Remove rows containing NaN values
    def remove_nan_rows(self) -> None:
        """
        Removes rows containing NaN values from the DataFrame.
        """
        try:
            self.df.dropna(inplace=True)
        except Exception as e:
            raise Exception(f"An error occurred while removing NaN rows: {str(e)}")

    # Variables

    # Delete a variable
    def delete_variable(self, name: str) -> None:
        """
        Deletes a variable from DataFrame.

        Args:
            name: Name of the variable to delete.
        """
        try:
            self.df.drop(columns=[name], inplace=True)
        except KeyError:
            raise KeyError(f"Variable '{name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while deleting the variable: {str(e)}")

    # Rename a variable
    def rename_variable(self, old_name: str, new_name: str) -> None:
        """
        Renames a variable in the DataFrame.

        Args:
            old_name (str): Old name of the variable.
            new_name (str): New name of the variable.
        """
        try:
            self.df.rename(columns={old_name: new_name}, inplace=True)
        except KeyError:
            raise KeyError(f"Variable '{old_name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while renaming the variable: {str(e)}")

    # Get the type of a variable
    def get_variable_type(self, name: str) -> str:
        """
        Gets the type of a variable.

        Args:
            name (str): Name of the variable.

        Returns:
            str: Type of the variable.
        """
        try:
            variable_type = self.df[name].dtype
            return self._translate_variable_type(variable_type)
        except KeyError:
            raise KeyError(f"Variable '{name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while getting variable type: {str(e)}")

    # Get types of variables
    def get_variable_types(self) -> dict:
        """
        Gets types of all variables in DataFrame.

        Returns:
            dict: Dictionary containing the data types of variables `name`: `type`.
        """
        try:
            v_types = dict()
            for variable in self.df.columns:
                v_types[variable] = self._translate_variable_type(self.df[variable].dtype)
            return v_types
        except Exception as e:
            raise Exception(f"An error occurred while getting variable types: {str(e)}")

    # Change the type of a variable
    def change_variable_type(self, name: str) -> None:
        """
        Changes the type of a variable to the opposite type.
        If the type is 'numerical', it is changed to 'categorical'.
        If the type is 'categorical' and the type matches a decimal number with a comma instead of a dot,
        all the numbers are changed to float and the type becomes 'numerical'.
        ex. 12,37 (categorical) -> 12.37 (numerical)

        Args:
            name (str): Name of the variable.
        """
        try:
            current_type = self.df[name].dtype.name
            translated_type = self._translate_variable_type(current_type)

            if translated_type == 'categorical':
                # Convert comma-separated decimal numbers to float
                self.df[name] = self.df[name].str.replace(',', '.').astype(float)
            else:
                # Convert categorical to numerical
                self.df[name] = self.df[name].astype('category')
        except KeyError:
            raise KeyError(f"Variable '{name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while changing variable type: {str(e)}")

    # Standardize a variable
    def normalize_std(self, variable_name: str) -> None:
        """
        Performs standard normalization on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        try:
            mean_value = self.df[variable_name].mean()
            std_value = self.df[variable_name].std()
            self.df[variable_name] = (self.df[variable_name] - mean_value) / std_value
        except KeyError:
            raise KeyError(f"Variable '{variable_name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while normalizing variable: {str(e)}")

    # Normalize a variable based on quantiles
    def normalize_q(self, variable_name: str) -> None:
        """
        Performs quantile-based normalization on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        try:
            q25 = self.df[variable_name].quantile(0.25)
            q75 = self.df[variable_name].quantile(0.75)
            self.df[variable_name] = (self.df[variable_name] - q25) / (q75 - q25)
        except KeyError:
            raise KeyError(f"Variable '{variable_name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while normalizing variable: {str(e)}")

    # Standardize the entire dataset (all numerical features)
    def standarize_dataset(self) -> None:
        """
        Standardizes all numerical features in the DataFrame.
        """
        try:
            for variable in self.df.columns:
                if self.get_variable_type(variable) == 'numerical':
                    self.normalize_std(variable)
        except Exception as e:
            raise Exception(f"An error occurred while standardizing dataset: {str(e)}")
        
    # Standardize the entire dataset (all numerical features)
    def q_normalize_dataset(self) -> None:
        """
        Quantile normalizes all numerical features in the DataFrame.
        """
        try:
            for variable in self.df.columns:
                if self.get_variable_type(variable) == 'numerical':
                    self.normalize_std(variable)
        except Exception as e:
            raise Exception(f"An error occurred while quantile normalizing dataset: {str(e)}")


    # One-Hot Encode a variable
    def one_hot_encode(self, variable_name: str) -> None:
        """
        Performs one-hot encoding on a variable.

        Args:
            variable_name (str): Name of the variable.
        """
        try:
            column = self.df[variable_name]
            encoded_df = pd.get_dummies(column, prefix=variable_name)

            # Encoding True and False to 0 and 1
            encoded_df = encoded_df.applymap(lambda x: 1 if x > 0 else 0)

            self.df.drop(columns=[variable_name], inplace=True)
            self.df = pd.concat([self.df, encoded_df], axis=1)
        except KeyError:
            raise KeyError(f"Variable '{variable_name}' not found in DataFrame.")
        except Exception as e:
            raise Exception(f"An error occurred while one-hot encoding: {str(e)}")


    # One-Hot Encode entire dataset
    def one_hot_all(self, variable_name: str) -> None:
        """
        Performs one-hot encoding on every categorial variable.

        """
        try:
            for variable in self.df.columns:
                if self._translate_variable_type(variable) == 'categorical':
                    self.one_hot_encode(variable_name=variable)

        except Exception as e:
            raise Exception(f"An error occurred while one-hot encoding: {str(e)}")
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
        try:
            pca_data = PCA(n_components=n_components)
            principal_components = pca_data.fit_transform(self.df)  # PCA Analysis

            pca_df = pd.DataFrame(data=principal_components, columns=None)  # Prepare PCA object

            return PCAHandler(pca_df)
        except Exception as e:
            raise Exception(f"An error occurred during PCA analysis: {str(e)}")
