from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QHBoxLayout, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt


class EditableHeaderTableWidget(QTableWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_instance = parent.data_instance # zapisanie poprzedniego stanu
        self.horizontalHeader().sectionDoubleClicked.connect(self.onHeaderDoubleClicked)
        self.line_edit = QLineEdit(self)
        self.line_edit.hide()
        self.line_edit.editingFinished.connect(self.onEditingFinished)

    def onHeaderDoubleClicked(self, section):
        header = self.horizontalHeader()
        # Ustawienie położenia i rozmiaru QLineEdit na nagłówku
        rect = header.sectionViewportPosition(section)
        self.line_edit.move(rect, 0)
        self.line_edit.resize(header.sectionSize(section), header.height())
        # Pobranie oryginalnej nazwy kolumny i ustawienie jej jako wartości początkowej QLineEdit
        self.line_edit.setText(header.model().headerData(section, Qt.Horizontal))
        self.line_edit.show()
        self.line_edit.setFocus()
        self.current_section = section  # Zapisanie aktualnie edytowanej sekcji

    def onEditingFinished(self):
        new_name = self.line_edit.text()
        self.line_edit.hide()  # Ukryj QLineEdit
        self.line_edit.clearFocus()  # Usuń fokus z QLineEdit
        # if not new_name:
        #     print("Please enter a new name.")
        #     return

        # Oryginalna nazwa zmiennej, którą zamierzamy zmienić
        old_name = self.horizontalHeaderItem(self.current_section).text()

        # Sprawdzenie, czy nowa nazwa jest różna od starej, aby uniknąć zbędnych operacji
        if old_name != new_name:
            print("Zapisywanie stanu przed zmianą nazwy kolumny.")
            # Zapisz poprzedni stan w DataManager przed dokonaniem zmiany
            self.data_instance.save()

            # Aktualizacja DataFrame w DataManager
            if old_name in self.data_instance.df.columns:
                self.data_instance.rename_variable(old_name, new_name)

                # Aktualizacja nagłówka w QTableWidget
                self.horizontalHeaderItem(self.current_section).setText(new_name)

                # Opcjonalnie: odświeżenie danych w tabeli, jeśli jest to konieczne
                #self.parent().display_data_in_table(self.data_instance.df)
            else:
                print(f"Error: Column '{old_name}' not found in DataFrame.")


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
        self.variable_name_combo = QComboBox()

        # Wypełnianie rozwijanej listy nazwami zmiennych
        self.variable_name_combo.addItems(self.data_instance.get_df().columns)

        form_layout.addWidget(self.variable_name_label)
        form_layout.addWidget(self.variable_name_combo)

        self.delete_button = QPushButton("Usuń")
        self.delete_button.clicked.connect(self.delete_variable)

        layout.addLayout(form_layout)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

    def delete_variable(self):
        variable_name = self.variable_name_combo.currentText()
        if variable_name:
            try:
                self.data_instance.save()
                self.data_instance.delete_variable(variable_name)
                self.parent().display_data_in_table(self.data_instance.get_df())
                QMessageBox.information(self, "Sukces", f"Zmienna '{variable_name}' została usunięta.")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć zmiennej: {e}")
        else:
            QMessageBox.warning(self, "Uwaga", "Proszę wybrać nazwę zmiennej do usunięcia.")

