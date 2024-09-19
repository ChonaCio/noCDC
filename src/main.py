import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QMessageBox, QCheckBox, QLabel

import connectionMenu

class noCDC(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setGeometry(100,100,250,250)
        self.setWindowTitle("No CDC")
        # starts in Option Menu
        self.optionsMenu()
        self.show()

    def optionsMenu(self):
        connection_button = QPushButton(self)
        connection_button.setText("Connections")
        connection_button.resize(250, 40)
        connection_button.clicked.connect(self.ConnectionsMenu)

        process_button = QPushButton(self)
        process_button.setText("Processes")
        process_button.resize(250, 40)
        process_button.move(0, 40)
        process_button.clicked.connect(self.processMenu)

    def ConnectionsMenu(self):
        self.conn_menu = connectionMenu.connectionMenu()
        self.conn_menu.show()

    def processMenu(self):
        print("Click")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    noCDC = noCDC()
    sys.exit(app.exec())