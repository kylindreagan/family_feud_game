from SpeechtoText import speech_to_text
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
import bluetooth
import sys
from qwindows import BluetoothDialog

class ClientJoiner(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI
    
    def initUI(self):
        self.setWindowTitle('Family Feud Multiplayer')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        self.join_button = QPushButton("Join Game", self)
        self.join_button.connect(self.join_game)
        main_layout.addWidget(self.join_button)

        self.setLayout(main_layout)

    
    def join_game(self, target_address):
        port = 1  # RFCOMM channel
        client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        host = self.find_host()
        if host == None:
            return
        
    
    def find_host(self):
        nearby_devices = bluetooth.discover_devices(lookup_names = True)
        devices = {}

        for addr, name in nearby_devices:
            devices[name] = addr
        
        device_names = devices.keys()
        dialog = BluetoothDialog(devices.keys())
        dialog.exec_()  # This will block until the dialog is closed
        host = dialog.get_data()
        return devices[host] if host in devices else None
        
        

def main():
    app = QApplication(sys.argv)
    ex = ClientJoiner()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()