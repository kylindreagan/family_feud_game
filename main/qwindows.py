from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Input Form")

        # Layout for the dialog
        self.layout = QFormLayout()

        # Create input fields (QLineEdit)
        self.input1 = QLineEdit(self)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Add widgets to the layout
        self.layout.addRow("Input 1:", self.input1)
        self.layout.addRow(self.submit_button)
        # Set the dialog's layout
        self.setLayout(self.layout)

        self.returned_data = None

    def on_submit(self):
        # Get the text input from the fields
        input1_value = self.input1.text()

        self.returned_data =  input1_value

        # Close the dialog
        self.accept()
    
    def get_data(self):
        return self.returned_data
