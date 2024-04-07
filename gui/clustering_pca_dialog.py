import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QComboBox, QVBoxLayout, QDialog, QLineEdit, QMessageBox, \
    QSpinBox, QWidget, QCheckBox, QFormLayout, QFileDialog
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.cluster import KMeans


# class PCADialog(QDialog):
#     def __init__(self, parent=None, default_n_components=None):
#         super().__init__(parent)
#         self.data_instance = parent.data_instance
#         # Użyj domyślnej liczby komponentów, jeśli jest dostarczona, w przeciwnym razie oblicz ją
#         self.default_n_components = default_n_components if default_n_components is not None else str(
#             len(self.data_instance.get_df().columns))
#         self.init_ui()
#
#     def init_ui(self):
#         self.setWindowTitle('Analiza PCA')
#         self.setGeometry(100, 100, 300, 200)  # Dostosowany rozmiar okna
#
#         layout = QVBoxLayout()
#         form_layout = QHBoxLayout()
#
#         self.components_label = QLabel("Liczba komponentów:")
#         self.components_input = QLineEdit()
#
#         # Ustaw domyślną liczbę komponentów
#         self.components_input.setText(self.default_n_components)
#
#         form_layout.addWidget(self.components_label)
#         form_layout.addWidget(self.components_input)
#
#         self.pca_button = QPushButton("Uruchom PCA")
#         self.pca_button.clicked.connect(self.run_pca)
#
#         layout.addLayout(form_layout)
#         layout.addWidget(self.pca_button)
#         self.setLayout(layout)
#
#     def run_pca(self):
#         try:
#             n_components = int(self.components_input.text())
#             if 0 < n_components <= len(self.data_instance.get_df().columns):
#                 self.parent().pca_handler = self.data_instance.PCA(n_components)
#                 self.parent().display_pca_results()  # Wyświetl wyniki analizy PCA
#                 self.parent().save_and_display_pca()  # Nowa metoda do wyświetlenia wykresu
#                 self.parent().pca_done = True
#                 self.close()
#             else:
#                 QMessageBox.critical("Podano niepoprawną liczba komponentów do analizy PCA.")
#         except ValueError as e:
#             QMessageBox.warning(self, "Wystąpił błąd - spróbuj ponownie")

class PCADialog(QDialog):
    def __init__(self, parent=None, default_n_components=None):
        super().__init__(parent)
        self.data_instance = parent.data_instance
        self.default_n_components = default_n_components if default_n_components is not None else str(
            len(self.data_instance.get_df().columns))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Analiza PCA')
        self.setGeometry(100, 100, 400, 200)  # Dostosowany rozmiar

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.components_label = QLabel("Liczba komponentów:")
        self.components_input = QLineEdit()
        self.components_input.setText(self.default_n_components)

        form_layout.addWidget(self.components_label)
        form_layout.addWidget(self.components_input)

        layout.addLayout(form_layout)

        self.pca_button = QPushButton("Uruchom PCA -> wybierz folder do zapisu wykresu i danych")
        self.pca_button.clicked.connect(self.run_pca)

        layout.addWidget(self.pca_button)
        self.setLayout(layout)

    def run_pca(self):
        n_components = self.components_input.text()

        if not n_components.isdigit() or not 0 < int(n_components) <= len(self.data_instance.get_df().columns):
            QMessageBox.warning(self, "Błąd", "Podano niepoprawną liczbę komponentów do analizy PCA.")
            return

        # Otwieranie dialogu wyboru folderu bezpośrednio przed uruchomieniem PCA
        directory = QFileDialog.getExistingDirectory(self, "Wybierz folder do zapisu wyników i wykresu PCA")
        if directory:  # Jeśli użytkownik wybierze folder
            try:
                n_components = int(n_components)
                self.parent().pca_handler = self.data_instance.PCA(n_components)
                # Przekazanie ścieżki do metody zapisującej wyniki i wykres PCA
                self.parent().save_and_display_pca(directory, self.parent().pca_handler.get_df())
                self.parent().pca_done = True
                QMessageBox.information(self, "Analiza PCA", "Analiza PCA została zakończona i wyniki zostały zapisane.")
                self.close()
            except ValueError as e:
                QMessageBox.warning(self, "Wystąpił błąd", "Spróbuj ponownie. Błąd: " + str(e))
        else:
            # Jeśli użytkownik nie wybierze folderu, wyświetl ostrzeżenie
            QMessageBox.warning(self, "Błąd", "Ścieżka do zapisu nie została wybrana. Analiza PCA nie zostanie uruchomiona.")


class PlotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Wyniki grupowania")
        self.setGeometry(100, 100, 800, 600)  # Możesz dostosować rozmiary okna

        # Tworzymy layout dla naszego dialogu
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tworzymy figurę dla wykresu
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot(self, pca_handler, x_component, y_component, title):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        ax.scatter(pca_handler.df[x_component], pca_handler.df[y_component], alpha=0.5, c=pca_handler.labels)
        ax.set_xlabel(x_component)
        ax.set_ylabel(y_component)
        ax.set_title(title)

        self.canvas.draw()


class KMeansSuggestionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pca_handler = parent.pca_handler
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Grupowanie KMeans')
        self.setGeometry(100, 100, 300, 200)  # Dostosowany rozmiar okna

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.max_clusters_input = QLineEdit()
        # self.draw_graph_checkbox = QCheckBox("Rysuj wykres")

        form_layout.addRow("Maksymalna liczba klastrów:", self.max_clusters_input)
        # form_layout.addRow(self.draw_graph_checkbox)

        self.run_button = QPushButton("Podaj optymalną liczbę klastrów wraz z wykresem")
        self.run_button.clicked.connect(self.run_suggestion)

        layout.addLayout(form_layout)
        layout.addWidget(self.run_button)
        self.setLayout(layout)

    def run_suggestion(self):
        max_clusters = self.max_clusters_input.text()
        # draw_graph = self.draw_graph_checkbox.isChecked()

        # Walidacja wejścia użytkownika
        if not max_clusters.isdigit() or int(max_clusters) < 2:
            QMessageBox.warning(self, "Błąd", "Maksymalna liczba klastrów musi być liczbą większą niż 1.")
            return

        max_clusters = int(max_clusters)

        try:
            # Zakładamy, że data_instance posiada metodę suggest_clusters_kmeans
            optimal_clusters = self.pca_handler.suggest_clusters_kmeans(max_clusters=max_clusters,
                                                                        draw_graph=True)
            QMessageBox.information(self, "Sugerowana liczba klastrów", f"Optymalna liczba klastrów: {optimal_clusters}")

            # if draw_graph:
            #     # Zakładamy, że metoda suggest_clusters_kmeans rysuje wykres, gdy draw_graph=True
            #     # Jeśli metoda nie rysuje wykresu bezpośrednio, można dodać logikę rysowania tutaj.
            #     pass
            # Kod do obliczenia optymalnej liczby klastrów...
            user_decision = QMessageBox.question(self, "Uruchom KMeans",
                                                 "Czy chcesz uruchomić klastrowanie KMeans z optymalną liczbą klastrów?",
                                                 QMessageBox.Yes | QMessageBox.No)

            if user_decision == QMessageBox.Yes:
                self.run_kmeans(optimal_clusters)  # Uruchamiamy KMeans z zasugerowaną liczbą klastrów

        except Exception as e:
            QMessageBox.critical(self, "Błąd",
                                 f"Wystąpił błąd podczas obliczania sugerowanej liczby klastrów.")

    def run_kmeans(self, optimal_clusters):
        try:
            self.parent().data_instance.save()
            self.pca_handler.kmeans_clustering(num_clusters=optimal_clusters)
            self.parent().kmeans_done = True
            QMessageBox.information(self, "KMeans Clustering",
                                    f"Klastrowanie KMeans zakończone dla {optimal_clusters} klastrów.")

            # Utworzenie instancji okna dialogowego i wyświetlenie wykresu
            plot_dialog = PlotDialog(self)
            plot_dialog.plot(self.pca_handler, 'pc1', 'pc2', f'Klastry KMeans dla {optimal_clusters} klastrów')
            plot_dialog.exec_()

        except ValueError as e:
            QMessageBox.critical(self, "Wystąpił błąd - spróbuj ponownie")
        except Exception as e:
            QMessageBox.critical(self, "Wystąpił błąd", f"Wystąpił nieoczekiwany błąd.")


class DBSCANDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pca_handler = parent.pca_handler  # Zakładamy, że PCA Handler jest dostępny w rodzicu
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Grupowanie DBSCAN')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        self.min_samples_input = QLineEdit()
        form_layout.addRow("Min samples:", self.min_samples_input)

        self.run_button = QPushButton("Zasugeruj i pokaż wykres")
        self.run_button.clicked.connect(self.run_dbscan_suggestion)
        layout.addLayout(form_layout)
        layout.addWidget(self.run_button)

    def run_dbscan_suggestion(self):
        min_samples = self.min_samples_input.text()
        if not min_samples.isdigit() or int(min_samples) <= 0:
            QMessageBox.warning(self, "Błąd", "Min samples musi być liczbą większą niż 0.")
            return

        min_samples = int(min_samples)
        try:
            optimal_eps = self.pca_handler.suggest_clusters_dbscan(min_samples=min_samples, draw_graph=True)
            QMessageBox.information(self, "Sugerowane EPS", f"Zasugerowana wartość optimal eps: {optimal_eps}")

            self.parent().data_instance.save()
            self.pca_handler.dbscan_clustering(eps=optimal_eps, min_samples=min_samples)
            self.parent().dbscan_done = True
            self.display_dbscan_results()

        except Exception as e:
            QMessageBox.critical(self, "Wystąpił błąd", f"Wystąpił błąd - spróbuj ponownie")

    def display_dbscan_results(self):
        plot_dialog = PlotDialog(self)
        plot_dialog.plot(self.pca_handler, 'pc1', 'pc2', 'DBSCAN Clusters')
        plot_dialog.exec_()
