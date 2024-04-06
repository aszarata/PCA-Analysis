import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget, QDialog, QHBoxLayout, QLineEdit, QMessageBox, QInputDialog, QFormLayout, QSpacerItem, \
    QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QComboBox
from matplotlib import pyplot as plt

from app_backend.data_manager import DataManager
from gui.variable_dialog import *
from gui.clustering_pca_dialog import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.table_widget = None
        self.label = None
        self.stacked_widget = QStackedWidget()
        self.data_instance = DataManager()
        self.init_ui()
        self.setAcceptDrops(True)  # Włączamy obsługę przeciągania i upuszczania pliku csv

    def init_ui(self):
        self.setWindowTitle('PCA Analysis')
        self.setGeometry(100, 100, 1200, 1000)

        self.init_welcome_page()
        self.init_import_page()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        self.init_data_manipulation_page()  # Inicjalizacja ekranu manipulacji danymi

    def init_welcome_page(self):
        welcome_page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Witamy w Aplikacji PCA Analysis")
        font = QFont()
        font.setPointSize(48)
        title.setFont(font)
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("font-size: 48px; color: #B0E0E6; font-family: Roboto;")

        logo = QLabel()
        pixmap = QPixmap("logo.png")
        logo.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)

        start_button = QPushButton("Rozpocznij")
        start_button.clicked.connect(self.go_to_import_page)

        layout.addWidget(title)

        # Luka przed elementami, aby wypchnąć je do środka
        spacer_before = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_before)

        layout.addWidget(logo)

        # Luka po elementach, aby utrzymać je na środku
        spacer_after = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_after)

        layout.addWidget(start_button)

        welcome_page.setLayout(layout)
        self.stacked_widget.addWidget(welcome_page)

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz plik csv", "", "Pliki csv (*.csv)", options=options)
        if file_name:
            # Pytanie o separator
            separator, ok = QInputDialog.getItem(self, "Wybierz separator", "Separator użyty w pliku CSV:", [",", ";"],
                                                 0, False)
            if ok and separator:
                try:
                    self.process_file(file_name, separator)
                except Exception as e:
                    QMessageBox.warning(self, "Błąd", f"Wystąpił błąd podczas przetwarzania pliku: {e}", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Anulowano", "Operacja otwarcia pliku została anulowana.", QMessageBox.Ok)

    def init_import_page(self):
        import_page = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel("Przeciągnij plik tutaj lub kliknij przycisk poniżej.")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        btn = QPushButton('Wybierz plik csv')
        btn.clicked.connect(self.open_file_name_dialog)
        layout.addWidget(btn)

        import_page.setLayout(layout)
        self.stacked_widget.addWidget(import_page)

    def init_data_manipulation_page(self):
        manipulation_page = QWidget()
        layout = QVBoxLayout()

        self.table_widget = EditableHeaderTableWidget(self)  # Używamy naszej niestandardowej klasy
        layout.addWidget(self.table_widget)

        # guzik do zmiany typu zmiennej
        change_type_button = QPushButton('Zmień typ zmiennej')
        change_type_button.clicked.connect(self.open_change_type_dialog)
        layout.addWidget(change_type_button)

        # guzik do usuwania nazwy zmiennej
        delete_button = QPushButton('Usuń zmienną')
        delete_button.clicked.connect(self.open_delete_dialog)
        layout.addWidget(delete_button)

        # guzik do resetu do stanu poczatkowego
        # Add reset button here
        reset_button = QPushButton('Resetuj dane do stanu początkowego')
        reset_button.clicked.connect(self.reset_data)
        layout.addWidget(reset_button)

        # guzik do cofania zmian do poprzednio zapisanego stanu
        undo_button = QPushButton('Cofnij ostatnią zmianę')
        undo_button.clicked.connect(self.undo_changes)
        layout.addWidget(undo_button)

        # # guzik do normalizacji_std
        # normalize_std_button = QPushButton('Normalizuj zmienną (standardowa normalizacja)')
        # normalize_std_button.clicked.connect(self.open_normalize_std_dialog)
        # layout.addWidget(normalize_std_button)

        # # guzik do normalizacji_q
        # normalize_q_button = QPushButton('Normalizuj zmienną (normalizacja oparta na kwantylu)')
        # normalize_q_button.clicked.connect(self.open_normalize_q_dialog)
        # layout.addWidget(normalize_q_button)

        # # guzik do standaryzacji/normalizacji calego zbioru danych
        # standarize_button = QPushButton('Normalizacja całego zbioru danych')
        # standarize_button.clicked.connect(self.open_standarize_dataset_dialog)
        # layout.addWidget(standarize_button)
        #
        # # guzik do one-hot-encode
        # onehot_encode_button = QPushButton('Metoda one-hot-encode dla zmiennej')
        # onehot_encode_button.clicked.connect(self.open_onehot_encode_dialog)
        # layout.addWidget(onehot_encode_button)

        # guzik do przygotowania do analizy pca -> one-hot-encode plus standaryzacja calego zbioru danych
        prepare_button = QPushButton('Przygotowanie danych do analizy PCA')
        prepare_button.clicked.connect(self.open_prepare_dialog)
        layout.addWidget(prepare_button)

        # # guzik do uruchamiania analizy PCA
        # pca_button = QPushButton('Uruchom Analizę PCA')
        # pca_button.clicked.connect(self.open_pca_dialog)
        # layout.addWidget(pca_button)

        # guzik do kmeans
        kmeans_button = QPushButton('Uruchom KMeans')
        kmeans_button.clicked.connect(self.open_kmeans_dialog)
        layout.addWidget(kmeans_button)

        # guzik do dbscan
        dbscan_button = QPushButton('Uruchom DBSCAN')
        dbscan_button.clicked.connect(self.open_dbscan_dialog)
        layout.addWidget(dbscan_button)

        manipulation_page.setLayout(layout)
        self.stacked_widget.addWidget(manipulation_page)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            valid = any(url.toLocalFile().endswith('.csv') for url in e.mimeData().urls())
            if valid:
                e.accept()
            else:
                e.ignore()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith('.csv'):
                self.process_file(path)

    def go_to_import_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def process_file(self, file_path, separator):
        if not file_path.lower().endswith('.csv'):
            self.label.setText('Zaimportowano nieobsługiwany format pliku. Proszę wybrać plik CSV.')
            return

        try:
            self.data_instance.read_from_csv(file_path, sep=separator)

            # Sprawdzanie, czy DataFrame ma więcej niż jedną kolumnę jako wskazówkę, że separator może być niewłaściwy
            if self.data_instance.df.shape[1] < 2:
                raise ValueError("Wygląda na to, że podano niewłaściwy separator. Proszę spróbować z innym.")

            self.stacked_widget.setCurrentIndex(2)
            self.display_data_in_table(self.data_instance.get_df())

        except ValueError as ve:
            QMessageBox.warning(self, "Błąd separatora", str(ve), QMessageBox.Ok)
        except Exception as e:
            print(f'Błąd przy przetwarzaniu pliku: {str(e)}')
            QMessageBox.warning(self, "Błąd",
                                f"Wystąpił błąd podczas przetwarzania pliku. Proszę sprawdzić format pliku oraz wybrany separator i spróbować ponownie.",
                                QMessageBox.Ok)

    def display_data_in_table(self, df):
        if df is None:
            df = self.data_instance.get_df()
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                # Zmiana flagi elementu, aby nie był edytowalny
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                # Ustawienie tekstu wskazówki (tooltip) z typem danych dla danej kolumny
                column_name = df.columns[j]
                column_data_type = self.data_instance.get_variable_type(
                    column_name)
                item.setToolTip(f"Typ: {column_data_type}")
                self.table_widget.setItem(i, j, item)

        self.table_widget.resizeColumnsToContents()

    def open_delete_dialog(self):
        self.delete_dialog = DeleteDialog(self)
        self.delete_dialog.show()

    def reset_data(self):
        self.data_instance.reset()
        self.display_data_in_table(self.data_instance.get_df())

    def undo_changes(self):
        try:
            self.data_instance.undo()
            self.display_data_in_table(self.data_instance.get_df())
            QMessageBox.information(self, "Cofnięto zmiany", "Zmiany zostały cofnięte do ostatniego zapisanego stanu.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się cofnąć zmian: {e}")

    def open_normalize_std_dialog(self):
        variable_name, ok = QInputDialog.getItem(self, "Wybierz zmienną do normalizacji", "Zmienna:",
                                                 self.data_instance.get_df().columns.tolist(), 0, False)
        if ok and variable_name:
            self.normalize_std_variable(variable_name)

    def normalize_std_variable(self, variable_name):
        try:
            self.data_instance.save()
            self.data_instance.normalize_std(variable_name)
            self.display_data_in_table(self.data_instance.get_df())
            QMessageBox.information(self, "Normalizacja", f"Zmienna '{variable_name}' została znormalizowana.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się znormalizować zmiennej: {e}")

    def open_normalize_q_dialog(self):
        variable_name, ok = QInputDialog.getItem(self, "Wybierz zmienną do normalizacji", "Zmienna:",
                                                 self.data_instance.get_df().columns.tolist(), 0, False)
        if ok and variable_name:
            self.normalize_q_variable(variable_name)

    def normalize_q_variable(self, variable_name):
        try:
            self.data_instance.save()
            self.data_instance.normalize_q(variable_name)
            self.display_data_in_table(self.data_instance.get_df())  # Refresh the table to show the normalized data
            QMessageBox.information(self, "Normalizacja", f"Zmienna '{variable_name}' została znormalizowana.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się znormalizować zmiennej: {e}")

    def open_prepare_dialog(self):
        # Pytanie wstępne do użytkownika
        confirmation_msg = QMessageBox()
        confirmation_msg.setWindowTitle("Potwierdzenie")
        confirmation_msg.setText("Czy jesteś pewien/pewna, \n"
                                 "że zmienne nieadekwatne do przeprowadzenia analizy PCA zostały przez Ciebie usunięte oraz \n"
                                 "że ustawiłeś/ustawiłaś typy wszystkich zmiennych na właściwe?")
        confirmation_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation_msg.setDefaultButton(QMessageBox.No)
        user_choice = confirmation_msg.exec_()

        # Kontynuuj tylko jeśli użytkownik wybrał 'Yes'
        if user_choice == QMessageBox.Yes:
            msgBox = QMessageBox()
            msgBox.setText("Wybierz rodzaj normalizacji")
            msgBox.addButton(QPushButton('Standardowa'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton('Oparta na kwantylach'), QMessageBox.NoRole)
            ret = msgBox.exec_()

            if ret == 0:
                self.prepare(normalization_type='std')
            elif ret == 1:
                self.prepare(normalization_type='quantile')
        else:
            # Użytkownik wybrał 'No', nic się nie dzieje
            return

    # def prepare(self):
    #     try:
    #         self.data_instance.save()
    #         for variable_name in self.data_instance.get_df().columns.tolist():
    #             if self.data_instance.get_variable_type(variable_name) == 'categorical':
    #                 self.data_instance.one_hot_encode(variable_name)
    #         self.data_instance.standarize_dataset()
    #         self.display_data_in_table(
    #         self.data_instance.get_df())  # Refresh the table to show the standardized data
    #         self.open_pca_dialog()
    #         QMessageBox.information(self, "Przygotowanie do PCA", "Cały zbiór danych został przygotowany do analizy PCA.")
    #     except Exception as e:
    #         QMessageBox.critical(self, "Błąd", f"Nie udało się przygotować zbioru danych do analizy PCA: {e}")

    def prepare(self, normalization_type):
        #QMessageBox.information(self, "Przygotowanie do analizy PCA",
        #                        "Zanim przystąpisz do procedury bezpośrednio związanej z obsługą analizy PCA, zmień typy zmiennych, jeśli uważasz to za konieczne, oraz usuń te niepotrzebne.")

        try:
            self.data_instance.remove_nan_rows()
            self.data_instance.save()

            # Kontynuacja przygotowań do PCA...
            n_components = len(self.data_instance.get_df().columns)

            if normalization_type == 'std':
                self.data_instance.standarize_dataset()
            else:
                self.data_instance.q_normalize_dataset()

            for variable_name in self.data_instance.get_df().columns.tolist():
                if self.data_instance.get_variable_type(variable_name) == 'categorical':
                    self.data_instance.one_hot_encode(variable_name)

            self.display_data_in_table(self.data_instance.get_df())  # Odśwież tabelę, aby pokazać przetworzone dane
            # Teraz przekazujemy liczbę komponentów jako argument do metody otwierającej dialog PCA
            self.open_pca_dialog(n_components)
            QMessageBox.information(self, "Przygotowanie do PCA",
                                    "Cały zbiór danych został przygotowany do analizy PCA.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się przygotować zbioru danych do analizy PCA: {e}")

    # def open_pca_dialog(self):
    #     self.pca_dialog = PCADialog(self)
    #     self.pca_dialog.show()

    def open_pca_dialog(self, default_n_components):
        # Tworzenie instancji dialogu PCA z domyślną liczbą komponentów
        pca_dialog = PCADialog(self)
        pca_dialog.components_input.setText(str(default_n_components))  # Ustawienie domyślnej liczby komponentów
        pca_dialog.show()

    # def display_pca_results(self, pca_handler):
    #     self.display_data_in_table(pca_handler.get_df())
    #
    #     # Uruchomienie dialogu z wynikami PCA
    #     pca_results_dialog = PCAResultsDialog(pca_handler, self)
    #     pca_results_dialog.exec_()

    # W klasie rodzica (np. główne okno aplikacji)
    def display_pca_plot(self, pca_handler):
        # Zakładając, że pca_handler jest instancją PCAHandler
        plt.figure(figsize=(10, 7))  # Ustawienie rozmiaru wykresu
        pca_handler.plot_2d('pc1', 'pc2',
                            'PCA - pierwsze dwa komponenty')  # Generowanie wykresu dla dwóch głównych komponentów

        # Zapisywanie wykresu w folderze, z którego wczytano dane
        if self.data_instance.last_file_path:  # Sprawdzanie, czy ścieżka do pliku została zapisana
            directory = os.path.dirname(self.data_instance.last_file_path)
            file_name = "PCA_plot.png"
            save_path = os.path.join(directory, file_name)
            plt.savefig(save_path)  # Zapisywanie wykresu
            print(f"Wykres został zapisany w: {save_path}")

        plt.show()  # Wyświetlenie wykresu

    def display_pca_results(self, pca_handler):
        # Przygotowanie okna dialogowego
        dialog = QDialog(self)
        dialog.setWindowTitle("Wyniki analizy PCA")
        dialog.setGeometry(100, 100, 600, 400)  # Zwiększony rozmiar dla lepszego wyświetlania tabeli
        layout = QVBoxLayout(dialog)

        # Tytuł
        title_label = QLabel("Wartości dla komponentów PCA:")
        layout.addWidget(title_label)

        # Pobranie DataFrame z pca_handler
        df = pca_handler.get_df()

        # Tworzenie tabeli do wyświetlenia danych
        table = QTableWidget(dialog)
        table.setColumnCount(len(df.columns))
        table.setRowCount(len(df.index))

        # Ustawianie nagłówków kolumn
        table.setHorizontalHeaderLabels(df.columns)

        # Wypełnianie tabeli danymi
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(f"{df.iloc[row, col]:.2f}")
                table.setItem(row, col, item)

        table.resizeColumnsToContents()  # Dostosowanie szerokości kolumn do zawartości
        layout.addWidget(table)

        # Dodawanie przycisku zamknięcia
        close_button = QPushButton("Wyświetl i zapisz wykres PCA")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def open_kmeans_dialog(self):
        pca_handler = self.data_instance.PCA(n_components=2)  # Można dostosować liczbę komponentów
        clustering_dialog = ClusteringResultsDialog(pca_handler, 'KMeans', self)
        clustering_dialog.exec_()

    def open_dbscan_dialog(self):
        pca_handler = self.data_instance.PCA(n_components=2)  # Można dostosować liczbę komponentów
        clustering_dialog = ClusteringResultsDialog(pca_handler, 'DBSCAN', self)
        clustering_dialog.exec_()

    # Funkcja obsługująca kliknięcie przycisku
    def open_change_type_dialog(self):
        variable_name, ok = QInputDialog.getItem(self, "Wybierz zmienną do zmiany typu", "Zmienna:",
                                                 self.data_instance.get_df().columns.tolist(), 0, False)
        if ok and variable_name:
            self.change_variable_type(variable_name)

    # Zmiana typu zmiennej
    def change_variable_type(self, variable_name):
        try:
            self.data_instance.change_variable_type(variable_name)
            self.display_data_in_table(self.data_instance.get_df())  # Odśwież tabelę, aby pokazać zmiany
            QMessageBox.information(self, "Zmiana typu", f"Typ zmiennej '{variable_name}' został zmieniony.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zmienić typu zmiennej: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    ex = MainWindow()
    #ex.setStyleSheet("QWidget { background-color: white }")
    ex.show()
    app.setStyleSheet("""
        QWidget { 
            background-color: white     
        }
        QWidget {
            font-size: 11px;
            font-family: Roboto;
        }
        QPushButton {
            background-color: #808000; 
            color: white;
            border-radius: 5px;
            padding: 3px;
            margin: 3px;
            font-family: Roboto;
        }
        QPushButton:hover {
            font-family: Roboto;
            background-color: #6B8E23; 
        }
        QTableWidget {
            font-family: Roboto;
            selection-background-color: #FF7F50; 
        }
        QTableWidget::item {
            color: #000000; 
            font-family: Roboto;
        }
        QTableWidget QHeaderView::section {
            color: #F28500; 
            padding: 5px;
            margin: 0px;
            font-weight: bold;
            font-family: Roboto;
        }
        QLabel {
            color: #DAA520; 
            font-family: Roboto;
        }
        QLineEdit, QComboBox {
        color: black; /* Ustawia kolor tekstu na czarny */
        font-family: Roboto;
        }
        QComboBox QAbstractItemView {
            color: black; /* Ustawia kolor tekstu elementów listy na czarny */
            selection-background-color: #FF7F50; /* Kolor tła dla zaznaczonych elementów */
            font-family: Roboto;
        }
    """)
    sys.exit(app.exec_())
