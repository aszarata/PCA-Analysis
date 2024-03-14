import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidgetItem, \
    QTableWidget, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import pandas as pd
from data import Data

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.stackedWidget = QStackedWidget()
        self.initUI()
        self.setAcceptDrops(True)  # Włączamy obsługę przeciągania i upuszczania pliku csv

    def initUI(self):
        self.setWindowTitle('PCA Analysis')
        self.setGeometry(100, 100, 400, 300)

        self.initWelcomePage()
        self.initImportPage()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.stackedWidget)
        self.setLayout(mainLayout)

    def initWelcomePage(self):
        welcomePage = QWidget()
        layout = QVBoxLayout()

        # Tworzenie etykiety
        title = QLabel("Witamy w Aplikacji PCA Analysis")
        # Ustawianie czcionki i rozmiaru
        font = QFont()
        font.setPointSize(24)
        title.setFont(font)
        # Wyśrodkowanie tekstu
        title.setAlignment(Qt.AlignHCenter)

        logo = QLabel()
        pixmap = QPixmap("logo.png")  # Załóż, że "logo.png" to ścieżka do pliku logo
        logo.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # Dostosuj rozmiar logo
        # Wyśrodkowanie obrazu w QLabel
        logo.setAlignment(Qt.AlignCenter)

        startButton = QPushButton("Rozpocznij")
        startButton.clicked.connect(self.goToImportPage)

        layout.addWidget(title)
        layout.addWidget(logo)
        layout.addWidget(startButton)
        welcomePage.setLayout(layout)

        self.stackedWidget.addWidget(welcomePage)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            self.processFile(path)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "",
                                                  "Wszystkie pliki (*);;Pliki tekstowe (*.txt)", options=options)
        if fileName:
            self.processFile(fileName)

    def initImportPage(self):
        importPage = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel("Przeciągnij plik tutaj lub kliknij przycisk poniżej.")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        btn = QPushButton('Wybierz plik')
        btn.clicked.connect(self.openFileNameDialog)
        layout.addWidget(btn)

        importPage.setLayout(layout)
        self.stackedWidget.addWidget(importPage)

    def goToImportPage(self):
        self.stackedWidget.setCurrentIndex(1)

    def processFile(self, filePath):
        # Sprawdź rozszerzenie pliku, czy to CSV
        if not filePath.lower().endswith('.csv'):
            self.label.setText('Zaimportowano nieobsługiwany format pliku. Proszę wybrać plik CSV.')
            return
        data_instance = Data()
        try:
            data_instance.read_from_csv(filePath)
            self.displayDataInTable(data_instance.display())

        except Exception as e:
            print(f'Błąd przy przetwarzaniu pliku: {str(e)}')

    def displayDataInTable(self, df):
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                # Zmiana flagi elementu, aby nie był edytowalny
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tableWidget.setItem(i, j, item)

        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
