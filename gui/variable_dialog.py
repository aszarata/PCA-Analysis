from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QHBoxLayout, QLineEdit


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
