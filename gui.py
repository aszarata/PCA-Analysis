import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QDropEvent, QDragEnterEvent
from app_backend.data_manager import DataManager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.table_widget = None
        self.label = None
        self.stacked_widget = QStackedWidget()
        self.init_ui()
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
        data_instance = DataManager()
        try:
            data_instance.read_from_csv(file_path)
            self.display_data_in_table(data_instance.get_df())

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
