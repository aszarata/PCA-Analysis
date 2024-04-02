from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QComboBox, QVBoxLayout, QDialog, QLineEdit
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class ClusteringResultsDialog(QDialog):
    def __init__(self, pca_handler, clustering_type, parent=None):
        super().__init__(parent)
        self.pca_handler = pca_handler
        self.clustering_type = clustering_type  # 'KMeans' lub 'DBSCAN'
        self.setWindowTitle(f'Wyniki Klasteringu: {self.clustering_type}')
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        if self.clustering_type == 'KMeans':
            self.pca_handler.kmeans_clustering(num_clusters=3)  # Tu można dodać dynamiczne wybieranie liczby klastrów
        elif self.clustering_type == 'DBSCAN':
            self.pca_handler.dbscan_clustering(eps=0.5,
                                               min_samples=5)  # Tu można dodać dynamiczne wybieranie parametrów

        self.pca_handler.plot_2d('pc1', 'pc2', f'{self.clustering_type} - Pierwsze dwa komponenty', ax=sc.axes)
        layout.addWidget(sc)

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

class PCAResultsDialog(QDialog):
    def __init__(self, pca_handler, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Wyniki Analizy PCA')
        self.setGeometry(100, 100, 600, 500)
        self.pca_handler = pca_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Dodajemy elementy UI do wyboru składowych PCA
        components_layout = QHBoxLayout()
        self.component_x_combo = QComboBox()
        self.component_y_combo = QComboBox()

        # Wypełniamy QComboBox możliwymi do wyboru składowymi
        components = [f'pc{i + 1}' for i in range(len(self.pca_handler.get_df().columns))]
        self.component_x_combo.addItems(components)
        self.component_y_combo.addItems(components)

        # Ustawiamy domyślnie wybrane opcje (pierwsze dwie składowe)
        self.component_x_combo.setCurrentIndex(0)
        self.component_y_combo.setCurrentIndex(1)

        components_layout.addWidget(QLabel("Składowa X:"))
        components_layout.addWidget(self.component_x_combo)
        components_layout.addWidget(QLabel("Składowa Y:"))
        components_layout.addWidget(self.component_y_combo)

        layout.addLayout(components_layout)

        # Przycisk do generowania wykresu
        plot_button = QPushButton('Generuj Wykres')
        plot_button.clicked.connect(self.update_plot)
        layout.addWidget(plot_button)

        # Tworzenie widgetu MplCanvas
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.sc)

        self.update_plot()  # Wygeneruj wykres przy pierwszym uruchomieniu

    def update_plot(self):
        x_component = self.component_x_combo.currentText()
        y_component = self.component_y_combo.currentText()

        # Wyczyść obecne osie przed generowaniem nowego wykresu
        self.sc.axes.clear()

        # Generowanie nowego wykresu dla wybranych składowych
        self.pca_handler.plot_2d(x_component, y_component, f'PCA - {x_component} vs {y_component}', ax=self.sc.axes)

        # Odświeżamy widget MplCanvas, aby wyświetlić nowy wykres
        self.sc.draw()

