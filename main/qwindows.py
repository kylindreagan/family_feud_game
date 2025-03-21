from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton

class QuestionDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Topic")

        # Layout for the dialog
        self.layout = QFormLayout()

        # Create input fields (QLineEdit)
        self.input1 = QLineEdit(self)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Add widgets to the layout
        self.layout.addRow("Enter a topic:", self.input1)
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

class FileDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File")

        # Layout for the dialog
        self.layout = QFormLayout()

        # Create input fields (QLineEdit)
        self.input1 = QLineEdit(self)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Add widgets to the layout
        self.layout.addRow("Enter name of file:", self.input1)
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

class AnswerDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Answer")

        # Layout for the dialog
        self.layout = QFormLayout()

        # Create input fields (QLineEdit)
        self.input1 = QLineEdit(self)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Add widgets to the layout
        self.layout.addRow("Enter your answer:", self.input1)
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

class HostDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Host")

        # Layout for the dialog
        self.layout = QFormLayout()

        # Create input fields (QLineEdit)
        self.input1 = QLineEdit(self)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Add widgets to the layout
        self.layout.addRow("Pick the closest answer (number of correct answer) or null if it's completely wrong:", self.input1)
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