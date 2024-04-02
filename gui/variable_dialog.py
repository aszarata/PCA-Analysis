from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QHBoxLayout, QLineEdit, QTableWidget,
                             QTableWidgetItem)
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
        # if not new_name:
        #     print("Please enter a new name.")
        #     return

        self.line_edit.hide()

        # Oryginalna nazwa zmiennej, którą zamierzamy zmienić
        old_name = self.horizontalHeaderItem(self.current_section).text()

        # Sprawdzenie, czy nowa nazwa jest różna od starej, aby uniknąć zbędnych operacji
        if old_name != new_name:
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
