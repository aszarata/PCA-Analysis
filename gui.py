import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget, QDialog, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QDropEvent, QDragEnterEvent
from app_backend.data_manager import DataManager


class RenameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance  # Ensure you have data_instance available in MainWindow
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
                self.data_instance.rename_variable(old_name, new_name)
                self.parent().display_data_in_table(self.data_instance.get_df())  # Refresh the table in MainWindow
                self.close()
            except Exception as e:
                print(f'Error renaming variable: {e}')
        else:
            print("Please enter both old and new names.")

class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance  # Access to DataManager instance
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
                self.data_instance.delete_variable(variable_name)
                self.parent().display_data_in_table(self.data_instance.get_df())  # Refresh the table in MainWindow
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", "Pliki csv (*.csv)", options=options)
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

        btn = QPushButton('Wybierz plik')
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
        reset_button = QPushButton('Resetuj dane')
        reset_button.clicked.connect(self.reset_data)
        layout.addWidget(reset_button)

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
        self.data_instance.reset()  # Call reset method from DataManager
        self.display_data_in_table(self.data_instance.get_df())  # Refresh the table to show the reset data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
