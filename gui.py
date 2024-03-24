import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget, QDialog, QHBoxLayout, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from app_backend.data_manager import DataManager


class PCAResultsDialog(QDialog):
    def __init__(self, pca_handler, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Wyniki Analizy PCA')
        self.setGeometry(100, 100, 600, 500)
        self.pca_handler = pca_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tworzenie widgetu MplCanvas
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.pca_handler.plot_2d('pc1', 'pc2', 'PCA - Pierwsze dwa komponenty', ax=sc.axes)

        layout.addWidget(sc)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class PCADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Analiza PCA')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.components_label = QLabel("Liczba komponentów:")
        self.components_input = QLineEdit()

        form_layout.addWidget(self.components_label)
        form_layout.addWidget(self.components_input)

        self.pca_button = QPushButton("Uruchom PCA")
        self.pca_button.clicked.connect(self.run_pca)

        layout.addLayout(form_layout)
        layout.addWidget(self.pca_button)
        self.setLayout(layout)

    def run_pca(self):
        n_components = int(self.components_input.text())
        if n_components > 0:
            self.data_instance.save()
            pca_handler = self.data_instance.PCA(n_components)
            self.parent().display_pca_results(pca_handler)
            self.close()
        else:
            print("Wprowadź poprawną liczbę komponentów.")


class TypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sprawdź typ zmiennej')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        self.variable_combo = QComboBox()
        self.variable_combo.addItems(self.data_instance.get_df().columns)

        self.type_label = QLabel("Typ: Nie wybrano")
        self.check_button = QPushButton("Sprawdź typ")
        self.check_button.clicked.connect(self.display_variable_type)

        layout.addWidget(self.variable_combo)
        layout.addWidget(self.type_label)
        layout.addWidget(self.check_button)

        self.setLayout(layout)

    def display_variable_type(self):
        variable_name = self.variable_combo.currentText()
        variable_type = self.data_instance.get_variable_type(variable_name)
        self.type_label.setText(f"Typ: {variable_type}")


class RenameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Zmień nazwę zmiennej')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.old_name_label = QLabel("Stara nazwa:")
        self.old_name_input = QLineEdit()

        self.new_name_label = QLabel("Nowa nazwa:")
        self.new_name_input = QLineEdit()

        form_layout.addWidget(self.old_name_label)
        form_layout.addWidget(self.old_name_input)
        form_layout.addWidget(self.new_name_label)
        form_layout.addWidget(self.new_name_input)

        self.rename_button = QPushButton("Zmień nazwę")
        self.rename_button.clicked.connect(self.rename_variable)

        layout.addLayout(form_layout)
        layout.addWidget(self.rename_button)
        self.setLayout(layout)

    def rename_variable(self):
        old_name = self.old_name_input.text()
        new_name = self.new_name_input.text()
        if old_name and new_name:
            try:
                self.data_instance.save()
                self.data_instance.rename_variable(old_name, new_name)
                self.parent().display_data_in_table(self.data_instance.get_df())
                self.close()
            except Exception as e:
                print(f'Error renaming variable: {e}')
        else:
            print("Please enter both old and new names.")


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Usuń zmienną')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.variable_name_label = QLabel("Nazwa zmiennej:")
        self.variable_name_input = QLineEdit()

        form_layout.addWidget(self.variable_name_label)
        form_layout.addWidget(self.variable_name_input)

        self.delete_button = QPushButton("Usuń")
        self.delete_button.clicked.connect(self.delete_variable)

        layout.addLayout(form_layout)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

    def delete_variable(self):
        variable_name = self.variable_name_input.text()
        if variable_name:
            try:
                self.data_instance.save()
                self.data_instance.delete_variable(variable_name)
                self.parent().display_data_in_table(self.data_instance.get_df())
                self.close()
            except Exception as e:
                print(f'Error deleting variable: {e}')
        else:
            print("Please enter the name of the variable to delete.")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.table_widget = None
        self.label = None
        self.stacked_widget = QStackedWidget()
        self.init_ui()
        self.data_instance = DataManager()
        self.setAcceptDrops(True)  # Włączamy obsługę przeciągania i upuszczania pliku csv

    def init_ui(self):
        self.setWindowTitle('PCA Analysis')
        self.setGeometry(100, 100, 400, 300)

        self.init_welcome_page()
        self.init_import_page()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def init_welcome_page(self):
        welcome_page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Witamy w Aplikacji PCA Analysis")
        font = QFont()
        font.setPointSize(24)
        title.setFont(font)
        title.setAlignment(Qt.AlignHCenter)

        logo = QLabel()
        pixmap = QPixmap("logo.png")
        logo.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)

        start_button = QPushButton("Rozpocznij")
        start_button.clicked.connect(self.go_to_import_page)

        layout.addWidget(title)
        layout.addWidget(logo)
        layout.addWidget(start_button)
        welcome_page.setLayout(layout)

        self.stacked_widget.addWidget(welcome_page)

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz plik csv", "", "Pliki csv (*.csv)", options=options)
        if file_name:
            self.process_file(file_name)

    def init_import_page(self):
        import_page = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel("Przeciągnij plik tutaj lub kliknij przycisk poniżej.")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        btn = QPushButton('Wybierz plik csv')
        btn.clicked.connect(self.open_file_name_dialog)
        layout.addWidget(btn)

        import_page.setLayout(layout)
        self.stacked_widget.addWidget(import_page)

        # guzik do zmiany nazwy zmiennej
        rename_button = QPushButton('Zmień nazwę zmiennej')
        rename_button.clicked.connect(self.open_rename_dialog)
        layout.addWidget(rename_button)

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

        # guzik do wyswietlenia nazwy zmiennej
        self.type_button = QPushButton('Sprawdź typ zmiennej')
        self.type_button.clicked.connect(self.open_type_dialog)
        layout.addWidget(self.type_button)

        # guzik do wyświetlania typów wszystkich zmiennych
        types_button = QPushButton('Pokaż typy wszystkich zmiennych')
        types_button.clicked.connect(self.display_variable_types)
        layout.addWidget(types_button)

        # guzik do normalizacji_std
        normalize_std_button = QPushButton('Normalizuj zmienną (standardowa normalizacja)')
        normalize_std_button.clicked.connect(self.open_normalize_std_dialog)
        layout.addWidget(normalize_std_button)

        # guzik do normalizacji_q
        normalize_q_button = QPushButton('Normalizuj zmienną (normalizacja oparta na kwantylu)')
        normalize_q_button.clicked.connect(self.open_normalize_q_dialog)
        layout.addWidget(normalize_q_button)

        # guzik do standaryzacji/normalizacji calego zbioru danych
        standarize_button = QPushButton('Normalizacja całego zbioru danych')
        standarize_button.clicked.connect(self.open_standarize_dataset_dialog)
        layout.addWidget(standarize_button)

        # guzik do one-hot-encode
        onehot_encode_button = QPushButton('Metoda one-hot-encode dla zmiennej')
        onehot_encode_button.clicked.connect(self.open_onehot_encode_dialog)
        layout.addWidget(onehot_encode_button)

        # guzik do uruchamiania analizy PCA
        pca_button = QPushButton('Uruchom Analizę PCA')
        pca_button.clicked.connect(self.open_pca_dialog)
        layout.addWidget(pca_button)

        import_page.setLayout(layout)
        self.stacked_widget.addWidget(import_page)

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

    def process_file(self, file_path):
        if not file_path.lower().endswith('.csv'):
            self.label.setText('Zaimportowano nieobsługiwany format pliku. Proszę wybrać plik CSV.')
            return

        try:
            # Próba wykrycia separatora poprzez odczytanie pierwszej linii pliku
            with open(file_path, 'r', encoding='utf-8') as file:
                first_line = file.readline()
                if ',' in first_line and ';' not in first_line:
                    sep = ','
                else:
                    sep = ';'

            self.data_instance.read_from_csv(file_path, sep=sep)  # Użycie wykrytego separatora
            self.display_data_in_table(self.data_instance.get_df())

        except Exception as e:
            print(f'Błąd przy przetwarzaniu pliku: {str(e)}')

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
                self.table_widget.setItem(i, j, item)

        self.table_widget.resizeColumnsToContents()

    def open_rename_dialog(self):
        self.rename_dialog = RenameDialog(self)
        self.rename_dialog.show()

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

    def open_type_dialog(self):
        self.type_dialog = TypeDialog(self)
        self.type_dialog.show()

    def display_variable_types(self):
        try:
            types = self.data_instance.get_variable_types()
            message = "Typy zmiennych:\n" + "\n".join([f"{var}: {typ}" for var, typ in types.items()])
            QMessageBox.information(self, "Typy Zmiennych", message)
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wyświetlić typów zmiennych: {e}")

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

    def open_standarize_dataset_dialog(self):
        reply = QMessageBox.question(self, 'Potwierdzenie', "Czy na pewno chcesz znormalizować cały zbiór danych?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.standarize_dataset()

    def standarize_dataset(self):
        try:
            self.data_instance.save()
            self.data_instance.standarize_dataset()
            self.display_data_in_table(self.data_instance.get_df())  # Refresh the table to show the standardized data
            QMessageBox.information(self, "Normalizacja", "Cały zbiór danych został znormalizowany.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się znormalizować zbioru danych: {e}")

    def open_onehot_encode_dialog(self):
        variable_name, ok = QInputDialog.getItem(self, "Wybierz zmienną dla metody one-hot-encode", "Zmienna:",
                                                 self.data_instance.get_df().columns.tolist(), 0, False)
        if ok and variable_name:
            self.onehot_encode(variable_name)

    def onehot_encode(self, variable_name):
        try:
            self.data_instance.save()
            self.data_instance.one_hot_encode(variable_name)
            self.display_data_in_table(
                self.data_instance.get_df())
            QMessageBox.information(self, "Kodowanie One-Hot",
                                    f"Zmienna '{variable_name}' została zakodowana metodą One-Hot.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd",
                                 f"Nie udało się zakodować zmiennej '{variable_name}' metodą One-Hot: {e}")

    def open_pca_dialog(self):
        self.pca_dialog = PCADialog(self)
        self.pca_dialog.show()

    def display_pca_results(self, pca_handler):
        self.display_data_in_table(pca_handler.get_df())

        # Uruchomienie dialogu z wynikami PCA
        pca_results_dialog = PCAResultsDialog(pca_handler, self)
        pca_results_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
