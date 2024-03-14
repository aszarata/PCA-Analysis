import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import Qt
import pandas as pd
from data import Data


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Import danych')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("Przeciągnij plik tutaj lub kliknij przycisk poniżej.")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        btn = QPushButton('Wybierz plik')
        btn.clicked.connect(self.openFileNameDialog)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.setAcceptDrops(True)

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

    def processFile(self, filePath):
        # Sprawdź rozszerzenie pliku, czy to CSV
        if not filePath.lower().endswith('.csv'):
            self.label.setText('Zaimportowano nieobsługiwany format pliku. Proszę wybrać plik CSV.')
            return

        # Utwórz instancję klasy Data i wczytaj plik CSV
        data_instance = Data()
        try:
            data_instance.read_from_csv(filePath)

            # Przykładowe działanie na danych
            data_instance.normalize_std('nazwa_kolumny')  # Normalizacja standardowa
            # data_instance.normalize_q('nazwa_kolumny')  # Normalizacja oparta o statystyki pozycyjne

            # Wyświetlenie pierwszych 5 wierszy danych w GUI
            self.label.setText(str(data_instance.display().head()))

        except Exception as e:
            self.label.setText(f'Błąd przy przetwarzaniu pliku: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
