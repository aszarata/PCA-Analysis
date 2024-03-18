import pandas as pd
from sklearn.decomposition import PCA


class PCADataMenager:

    def __init__(self, data: pd.DataFrame=None)-> None:
        self.input_df = data
        self.df = data

        # DataFrame jedną operację wstecz
        self.df_last = data

    # Główne funkcje

    # Wczytanie z pliku csv
    def read_from_csv(self, filename: str, sep: str=';', header: int=0) -> None:
        self.input_df = pd.read_csv(filename, sep=sep, header=header)
        self.input_df.columns = self.input_df.columns.astype(str)
        self.df = self.input_df.copy()

    # Wyswietlenie dataframe
    def display(self) -> pd.DataFrame:
        return self.df

    # Przywrócenie do stanu wejściowego
    def reset(self) -> None:
        self.df = self.input_df.copy()

    # Reset do ostatnio zapisanego stanu
    def undo(self) -> None:
        self.df = self.df_last.copy()

    # Zapisanie aktualnego stanu do zmiennej df_last
    def save(self) -> None:
        self.df_last = self.df.copy()    


    # Zmienne

    # Zmiana nazwy zmiennej
    def rename_variable(self, old_name: str, new_name: str) -> None:
        self.df.rename(columns={old_name: new_name}, inplace=True)

    # Typ jednej zmiennej
    def get_variable_type(self, name: str) -> str:
        variable_type = self.df[name].dtype
        return self._translate_variable_type(variable_type) # Wybór nazwy typu zmiennej
        
    # Typy zmiennych
    def get_variable_types(self):
        return self.df.dtypes

    # Normalizacja standardowa zmiennej
    def normalize_std(self, variable_name: str) -> None:
        mean_value = self.df[variable_name].mean()
        std_value = self.df[variable_name].std()
        self.df[variable_name] = (self.df[variable_name] - mean_value) / std_value

    # Normalizacja zmiennej oparta o statystyki pozycyjne
    def normalize_q(self, variable_name: str) -> None:
        q25 = self.df[variable_name].quantile(0.25)
        q75 = self.df[variable_name].quantile(0.75)
        self.df[variable_name] = (self.df[variable_name] - q25) / (q75 - q25)

    # Standaryzacja calego zbioru danych (wszystkie cechy nueryczne)
    def standarize_dataset(self) -> None:
        for variable in self.df.columns:
            if self.get_variable_type(variable) == 'numerical':
                self.normalize_std(variable)

    # One-Hot Ecoding zmiennej
    def one_hot_encode(self, variable_name: str) -> None:

        column = self.df[variable_name]
        encoded_df = pd.get_dummies(column, prefix=variable_name)

        # kodowanie True i False na 0 i 1
        encoded_df = encoded_df.applymap(lambda x: 1 if x > 0 else 0)
        
        self.df.drop(columns=[variable_name], inplace=True)
        self.df = pd.concat([self.df, encoded_df], axis=1)

    # Funkcje pomocnicze
    # Przetłumaczenie nazwy typu zmiennej z nazwy pandasowej
    def _translate_variable_type(self, variable_type: str) -> str:
        if variable_type != 'object':
            return 'numerical'
        return 'categorial'
    

        # PCA
    
    # Funkcja wykonujaca anlize PCA zwracająca osobny obiekt PCADataMenager.
    def PCA(self, n_components: int) -> object:
        pca_data = PCA(n_components=n_components)
        principal_components = pca_data.fit_transform(self.df)
        columns = [f'pc{i}' for i in range(n_components)]
        pca_df = pd.DataFrame(data=principal_components, columns=columns)

        return PCADataMenager(pca_df)

