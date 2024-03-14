import pandas as pd

class Data:

    def __init__(self):
        self.input_df = None
        self.df = None

    # Wyswietlenie dataframe
    def display(self) -> pd.DataFrame:
        return self.df

    # Wczytanie z pliku csv
    def read_from_csv(self, filename: str, sep=';') -> None:
        self.input_df = pd.read_csv(filename, sep=sep)
        self.df = self.input_df.copy()

    # Przywrócenie do stanu faktycznego
    def reset(self) -> None:
        self.df = self.input_df.copy()

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


