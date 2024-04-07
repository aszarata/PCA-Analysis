import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget, QDialog, QHBoxLayout, QLineEdit, QMessageBox, QInputDialog, QFormLayout, QSpacerItem, \
    QSizePolicy, QBoxLayout
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
        self.pca_handler = None
        self.pca_done = False
        self.kmeans_done = False
        self.dbscan_done = False
        self.pca_done = False
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
        start_button.setFixedSize(400, 80)
        start_button.clicked.connect(self.go_to_import_page)
        layout.addWidget(start_button, 0, Qt.AlignCenter)

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
        btn.setStyleSheet("QPushButton { width: 100px; height: 100px; }")
        layout.addWidget(btn)

        import_page.setLayout(layout)
        self.stacked_widget.addWidget(import_page)

    def init_data_manipulation_page(self):
        manipulation_page = QWidget()
        # Ustawienie głównego układu pionowego
        main_layout = QVBoxLayout()

        # Ustawienie poziomego układu dla guzików kwadratowych
        buttons_layout = QHBoxLayout()

        self.table_widget = EditableHeaderTableWidget(self)  # Używamy naszej niestandardowej klasy
        buttons_layout.addWidget(self.table_widget)

        # # guzik do resetu do stanu poczatkowego
        # reset_button = QPushButton('Resetuj dane do stanu początkowego')
        # reset_button.clicked.connect(self.reset_data)
        # layout.addWidget(reset_button)
        #
        # # guzik do cofania zmian do poprzednio zapisanego stanu
        # undo_button = QPushButton('Cofnij ostatnią zmianę')
        # undo_button.clicked.connect(self.undo_changes)
        # layout.addWidget(undo_button)
        #
        # # guzik do zmiany typu zmiennej
        # change_type_button = QPushButton('Zmień typ zmiennej')
        # change_type_button.clicked.connect(self.open_change_type_dialog)
        # layout.addWidget(change_type_button)
        #
        # # guzik do usuwania nazwy zmiennej
        # delete_button = QPushButton('Usuń zmienną')
        # delete_button.clicked.connect(self.open_delete_dialog)
        # layout.addWidget(delete_button)

        # Stworzenie i stylizacja guzika reset
        reset_button = QPushButton('Resetuj dane')
        reset_button.clicked.connect(self.reset_data)
        reset_button.setStyleSheet("QPushButton { width: 100px; height: 100px; }")  # Ustawia wymiary kwadratowe
        buttons_layout.addWidget(reset_button)

        # Stworzenie i stylizacja guzika undo
        undo_button = QPushButton('Cofnij zmianę')
        undo_button.clicked.connect(self.undo_changes)
        undo_button.setStyleSheet("QPushButton { width: 100px; height: 100px; }")  # Ustawia wymiary kwadratowe
        buttons_layout.addWidget(undo_button)

        # Stworzenie i stylizacja guzika do zmiany typu
        change_type_button = QPushButton('Zmień typ')
        change_type_button.clicked.connect(self.open_change_type_dialog)
        change_type_button.setStyleSheet("QPushButton { width: 100px; height: 100px; }")  # Ustawia wymiary kwadratowe
        buttons_layout.addWidget(change_type_button)

        # Stworzenie i stylizacja guzika do usuwania nazwy zmiennej
        delete_button = QPushButton('Usuń zmienną')
        delete_button.clicked.connect(self.open_delete_dialog)
        delete_button.setStyleSheet("QPushButton { width: 100px; height: 100px; }")  # Ustawia wymiary kwadratowe
        buttons_layout.addWidget(delete_button)

        # # guzik do przygotowania do analizy pca -> one-hot-encode plus standaryzacja calego zbioru danych
        # prepare_button = QPushButton('Analiza PCA')
        # prepare_button.clicked.connect(self.open_prepare_dialog)
        # layout.addWidget(prepare_button)
        #
        # # guzik do uruchamiania algorytmu KMeans z sugestią liczby klastrów
        # kmeans_suggestion_button = QPushButton('Grupowanie KMeans')
        # kmeans_suggestion_button.clicked.connect(self.open_kmeans_suggestion_dialog)
        # layout.addWidget(kmeans_suggestion_button)
        #
        # # guzik do uruchamiania algorytmu DBSCAN
        # dbscan_clustering_button = QPushButton('Grupowanie DBSCAN')
        # dbscan_clustering_button.clicked.connect(self.open_dbscan_dialog)
        # layout.addWidget(dbscan_clustering_button)

        # Dodanie układu z guzikami kwadratowymi do głównego układu
        main_layout.addLayout(buttons_layout)

        # Stworzenie i dodanie duzego guzika "Przygotowanie do PCA"
        pca_button = QPushButton('Przygotowanie do PCA')
        pca_button.clicked.connect(self.open_prepare_dialog)
        pca_button.setStyleSheet(
            "QPushButton { min-width: 400px; min-height: 50px; }")  # Ustawia większe wymiary dla duzego guzika
        main_layout.addWidget(pca_button)

        # guzik do uruchamiania algorytmu KMeans z sugestią liczby klastrów
        kmeans_suggestion_button = QPushButton('Grupowanie KMeans')
        kmeans_suggestion_button.clicked.connect(self.open_kmeans_suggestion_dialog)
        kmeans_suggestion_button.setStyleSheet(
            "QPushButton { min-width: 400px; min-height: 50px; }")  # Ustawia większe wymiary dla duzego guzika
        main_layout.addWidget(kmeans_suggestion_button)

        # guzik do uruchamiania algorytmu DBSCAN
        dbscan_clustering_button = QPushButton('Grupowanie DBSCAN')
        dbscan_clustering_button.clicked.connect(self.open_dbscan_dialog)
        dbscan_clustering_button.setStyleSheet(
            "QPushButton { min-width: 400px; min-height: 50px; }")  # Ustawia większe wymiary dla duzego guzika
        main_layout.addWidget(dbscan_clustering_button)

        manipulation_page.setLayout(main_layout)
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
                QMessageBox.critical(self, "Wygląda na to, że podano niewłaściwy separator. Proszę spróbować z innym.")

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
        try:
            self.data_instance.reset()
            #self.pca_done = False
            self.pca_done = False
            self.kmeans_done = False
            self.dbscan_done = False
            self.display_data_in_table(self.data_instance.get_df())
            QMessageBox.information(self, "Reset danych", "Dane zostały zresetowane do stanu początkowego.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zresetować danych.")

    def undo_changes(self):
        try:
            self.data_instance.undo()
            self.display_data_in_table(self.data_instance.get_df())
            QMessageBox.information(self, "Cofnięto zmiany", "Zmiany zostały cofnięte do ostatniego zapisanego stanu.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się cofnąć zmian.")

    def open_prepare_dialog(self):
        if self.pca_done:
            QMessageBox.warning(self, "Operacja niemożliwa",
                                "Analiza PCA została już wykonana. Jeśli chcesz wykonać ją ponownie proszę zresetować dane.")
            return
        # Pytanie wstępne do użytkownika
        confirmation_msg = QMessageBox()
        confirmation_msg.setWindowTitle("Potwierdzenie")
        confirmation_msg.setText("Czy jesteś pewien/pewna, \n"
                                 "że zmienne nieadekwatne do przeprowadzenia analizy PCA zostały przez Ciebie usunięte oraz \n"
                                 "że ustawiłeś/ustawiłaś typy wszystkich zmiennych na właściwe?\n"
                                 "\n"
                                 "Aby analiza PCA działała poprawnie, to dla wszystkich danych numerycznych które w zapisie mają przecinek dziesiętny -> zmień typ zmiennej\n"
                                 "\n"
                                 "Jeśli wskażesz 'yes',\n"
                                 "to na aktualnie wyświetlonych danych uruchomisz analizę PCA.")
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

    def prepare(self, normalization_type):
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

    def open_pca_dialog(self, default_n_components):
        # Tworzenie instancji dialogu PCA z domyślną liczbą komponentów
        pca_dialog = PCADialog(self)
        pca_dialog.components_input.setText(str(default_n_components))  # Ustawienie domyślnej liczby komponentów
        pca_dialog.show()

    # W klasie rodzica (np. główne okno aplikacji)
    # def display_pca_plot(self):
    #     # Zakładając, że pca_handler jest instancją PCAHandler
    #     plt.figure(figsize=(10, 7))  # Ustawienie rozmiaru wykresu
    #     self.pca_handler.plot_2d('pc1', 'pc2',
    #                         'PCA - pierwsze dwa komponenty')  # Generowanie wykresu dla dwóch głównych komponentów
    #
    #     # Zapisywanie wykresu w folderze, z którego wczytano dane
    #     if self.data_instance.last_file_path:  # Sprawdzanie, czy ścieżka do pliku została zapisana
    #         directory = os.path.dirname(self.data_instance.last_file_path)
    #         file_name = "PCA_plot.png"
    #         save_path = os.path.join(directory, file_name)
    #         plt.savefig(save_path)  # Zapisywanie wykresu
    #         print(f"Wykres został zapisany w: {save_path}")
    #
    #     plt.show()  # Wyświetlenie wykresu
    #
    # def display_pca_results(self):
    #     # Przygotowanie okna dialogowego
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Wyniki analizy PCA")
    #     dialog.setGeometry(100, 100, 600, 400)  # Zwiększony rozmiar dla lepszego wyświetlania tabeli
    #     layout = QVBoxLayout(dialog)
    #
    #     # Tytuł
    #     title_label = QLabel("Wartości dla komponentów PCA:")
    #     layout.addWidget(title_label)
    #
    #     # Pobranie DataFrame z pca_handler
    #     df = self.pca_handler.get_df()
    #
    #     # Tworzenie tabeli do wyświetlenia danych
    #     table = QTableWidget(dialog)
    #     table.setColumnCount(len(df.columns))
    #     table.setRowCount(len(df.index))
    #
    #     # Ustawianie nagłówków kolumn
    #     table.setHorizontalHeaderLabels(df.columns)
    #
    #     # Wypełnianie tabeli danymi
    #     for row in range(df.shape[0]):
    #         for col in range(df.shape[1]):
    #             item = QTableWidgetItem(f"{df.iloc[row, col]:.2f}")
    #             table.setItem(row, col, item)
    #
    #     table.resizeColumnsToContents()  # Dostosowanie szerokości kolumn do zawartości
    #     layout.addWidget(table)
    #
    #     # Dodawanie przycisku zamknięcia
    #     close_button = QPushButton("Wyświetl i zapisz wykres PCA")
    #     close_button.clicked.connect(dialog.close)
    #     layout.addWidget(close_button)
    #
    #     dialog.setLayout(layout)
    #     dialog.exec_()

    def display_pca_results(self):
        # Przygotowanie okna dialogowego
        dialog = QDialog(self)
        dialog.setWindowTitle("Wyniki analizy PCA")
        dialog.setGeometry(100, 100, 600, 600)  # Zwiększony rozmiar dla dodatkowych elementów

        layout = QVBoxLayout(dialog)

        # Tytuł
        title_label = QLabel("Wartości dla komponentów PCA:")
        layout.addWidget(title_label)

        # Pobranie DataFrame z pca_handler
        df = self.pca_handler.get_df()

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

        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Pole do wprowadzenia ścieżki zapisu
        save_path_input = QLineEdit(dialog)
        save_path_input.setPlaceholderText("Wprowadź ścieżkę do zapisu...")
        if self.data_instance.last_file_path:  # Domyślna ścieżka
            save_path_input.setText(os.path.dirname(self.data_instance.last_file_path))
        layout.addWidget(save_path_input)

        # Dodawanie przycisku zapisu i wyświetlenia
        save_and_show_button = QPushButton("Wyświetl wykres i zapisz aktualną wersję pliku")
        layout.addWidget(save_and_show_button)

        # Zmiana w akcji przycisku, aby teraz wywołać metodę wybierającą folder
        save_and_show_button.clicked.connect(self.prompt_save_folder_and_display_pca)

        dialog.setLayout(layout)
        dialog.exec_()

    def prompt_save_folder_and_display_pca(self):
        # Użytkownik wybiera folder
        save_path = QFileDialog.getExistingDirectory(self, "Wybierz folder do zapisu")
        if save_path:
            # Jeśli folder został wybrany, przekazujemy tę ścieżkę wraz z DataFrame do metody zapisu
            self.save_and_display_pca(save_path, self.pca_handler.get_df())
        else:
            QMessageBox.warning(self, "Błąd", "Nie wybrano folderu do zapisu.")

    # def save_and_display_pca(self, save_path, df):
    #     # Proces zapisu danych i wykresu wykorzystujący wybraną ścieżkę
    #     if not save_path:
    #         QMessageBox.warning(self, "Błąd", "Ścieżka do zapisu nie może być pusta.")
    #         return
    #
    #     # Zapis DataFrame do pliku .csv
    #     csv_file_path = os.path.join(save_path, "PCA_data.csv")
    #     self.display_pca_csv_results(csv_file_path)  # Wywołanie nowej metody do wyświetlenia wyników
    #     try:
    #         df.to_csv(csv_file_path, index=False)
    #         QMessageBox.information(self, "Zapisano dane", f"Dane PCA zostały zapisane do: {csv_file_path}")
    #     except Exception as e:
    #         QMessageBox.critical(self, "Błąd zapisu danych", f"Nie udało się zapisać danych: {str(e)}")
    #
    #     # Wyświetlenie i zapis wykresu PCA
    #     plt.figure(figsize=(10, 7))
    #     self.pca_handler.plot_2d('pc1', 'pc2', 'PCA - pierwsze dwa komponenty')
    #     plot_file_path = os.path.join(save_path, "PCA_plot.png")
    #     try:
    #         plt.savefig(plot_file_path)
    #         QMessageBox.information(self, "Zapisano wykres", f"Wykres PCA został zapisany do: {plot_file_path}")
    #         plt.show()  # Opcjonalnie wyświetlenie wykresu
    #     except Exception as e:
    #         QMessageBox.critical(self, "Błąd zapisu wykresu", f"Nie udało się zapisać wykresu: {str(e)}")

    def save_and_display_pca(self, save_path, df):
        # Debug: wydrukuj ścieżkę do sprawdzenia
        print(f"Ścieżka do zapisu: {save_path}")

        if not save_path:
            QMessageBox.warning(self, "Błąd", "Ścieżka do zapisu nie może być pusta.")
            return

        # Zapis DataFrame do pliku .csv
        csv_file_path = os.path.join(save_path, "PCA_data.csv")
        # Dodatkowe wydrukowanie ścieżki pliku CSV dla debugowania
        print(f"Ścieżka do pliku CSV: {csv_file_path}")

        try:
            df.to_csv(csv_file_path, index=False)
            QMessageBox.information(self, "Zapisano dane", f"Dane PCA zostały zapisane do: {csv_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu danych", f"Nie udało się zapisać danych: {str(e)}")
            return  # Dodano return, aby przerwać działanie metody w przypadku błędu

        # Wyświetlenie i zapis wykresu PCA
        plt.figure(figsize=(10, 7))
        self.pca_handler.plot_2d('pc1', 'pc2', 'PCA - pierwsze dwa komponenty')
        plot_file_path = os.path.join(save_path, "PCA_plot.png")
        # Dodatkowe wydrukowanie ścieżki pliku wykresu dla debugowania
        print(f"Ścieżka do pliku wykresu: {plot_file_path}")

        try:
            plt.savefig(plot_file_path)
            QMessageBox.information(self, "Zapisano wykres", f"Wykres PCA został zapisany do: {plot_file_path}")
            plt.show()  # Opcjonalnie wyświetlenie wykresu
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu wykresu", f"Nie udało się zapisać wykresu: {str(e)}")

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
            QMessageBox.critical(self, "Błąd", f"Nie udało się zmienić typu wskazanej zmiennej.")

    def open_kmeans_suggestion_dialog(self):
        # Sprawdzenie, czy analiza PCA została wykonana
        if not hasattr(self, 'pca_done') or not self.pca_done:
            QMessageBox.warning(self, "Błąd",
                                "Analiza PCA nie została zrealizowana. Proszę najpierw wykonać analizę PCA.")
        if self.kmeans_done:
            QMessageBox.warning(self, "Operacja niemożliwa",
                                "Grupowanie KMeans zostało już wykonane. Jeśli chcesz wykonać ją ponownie proszę zresetować dane.")
            return
        else:
            dialog = KMeansSuggestionDialog(self)
            dialog.exec_()

    def open_dbscan_dialog(self):
        # Sprawdzenie, czy analiza PCA została wykonana
        if not hasattr(self, 'pca_done') or not self.pca_done:
            QMessageBox.warning(self, "Błąd",
                                "Analiza PCA nie została zrealizowana. Proszę najpierw wykonać analizę PCA.")
        if self.dbscan_done:
            QMessageBox.warning(self, "Operacja niemożliwa",
                                "Grupowanie DBSCAN zostało już wykonane. Jeśli chcesz wykonać ją ponownie proszę zresetować dane.")
            return
        else:
            dialog = DBSCANDialog(self)
            dialog.exec_()

    def display_pca_csv_results(self, file_path):
        # Tworzenie okna dialogowego
        dialog = QDialog(self)
        dialog.setWindowTitle("Wyniki analizy PCA z pliku CSV")
        dialog.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Tworzenie i konfiguracja QTableWidget
        table = QTableWidget(dialog)
        layout.addWidget(table)

        # Wczytywanie danych z pliku CSV
        df = pd.read_csv(file_path)

        # Ustawianie liczby wierszy i kolumn na podstawie DataFrame
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        # Wypełnianie tabeli danymi
        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table.setItem(i, j, item)

        table.resizeColumnsToContents()

        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
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
