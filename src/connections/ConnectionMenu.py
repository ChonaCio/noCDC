import sys
import configparser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from ConnectionConfig import ConnectionConfig  # Import ConnectionConfig from another file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NoCDC - Connections")
        self.setGeometry(100, 100, 660, 600)
        self.ini_file = "data/connections.ini"

        # Initialize UI components
        self.init_ui()
        self.load_data()
        self.resize_table_columns()  # Resize columns after the table is loaded

    def init_ui(self):
        self.main_layout = QVBoxLayout()

        # Top bar with a search box and buttons
        top_bar_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.filter_table)
        top_bar_layout.addWidget(self.search_box)

        # Refresh button with image
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("img/icons/arrow-round_path.svg"))
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.clicked.connect(self.load_data)
        top_bar_layout.addWidget(self.refresh_button)

        # Add button with image
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon("img/icons/plus_path.svg"))
        self.add_button.setFixedSize(32, 32)
        self.add_button.clicked.connect(self.open_add_connection_window)
        top_bar_layout.addWidget(self.add_button)

        self.main_layout.addLayout(top_bar_layout)

        # Table view
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(5)  # Adjust column count for the action column
        self.table_view.setHorizontalHeaderLabels(["ID", "Type", "Host", "Database", "Action"])
        self.main_layout.addWidget(self.table_view)

        # Set layout to central widget
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_data(self):
        """Load data from ini file and populate the table."""
        self.config = configparser.ConfigParser()
        self.config.read(self.ini_file)

        self.table_view.setRowCount(0)  # Clear existing rows

        type_mapping = {
            'oracle': 'Oracle',
            'postgresql': 'Postgresql',
            'microsoftsqlserver': 'Microsoft SQL Server',
            'mysql': 'MySQL',
            'snowflake': 'Snowflake'
        }

        for section in self.config.sections():
            row_position = self.table_view.rowCount()
            self.table_view.insertRow(row_position)
            # Add ID, Type, Host, Database columns
            self.table_view.setItem(row_position, 0, QTableWidgetItem(section))
            self.table_view.setItem(row_position, 1, QTableWidgetItem(type_mapping[self.config[section].get('type', '')]))
            self.table_view.setItem(row_position, 2, QTableWidgetItem(self.config[section].get('host', '')))
            self.table_view.setItem(row_position, 3, QTableWidgetItem(self.config[section].get('database', '')))

            # Create a widget to contain the action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

            # Add edit button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("img/icons/edit_path.svg"))
            edit_button.setFixedSize(24, 24)
            edit_button.clicked.connect(lambda checked, id=section: self.open_edit_connection_window(id))
            action_layout.addWidget(edit_button)

            # Add delete button
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("img/icons/trash-1_path.svg"))
            delete_button.setFixedSize(24, 24)
            delete_button.clicked.connect(lambda checked, id=section: self.delete_connection(id))
            action_layout.addWidget(delete_button)

            action_widget.setLayout(action_layout)
            self.table_view.setCellWidget(row_position, 4, action_widget)

    def resize_table_columns(self):
        """Resize table columns based on the window size."""
        total_width = self.table_view.width()

        action_column_width = 100  # Fixed width for the "Action" column
        remaining_width = total_width - action_column_width - 15

        # Distribute remaining width among the first four columns
        self.table_view.setColumnWidth(0, int(remaining_width * 0.2))  # ID column
        self.table_view.setColumnWidth(1, int(remaining_width * 0.3))  # Type column
        self.table_view.setColumnWidth(2, int(remaining_width * 0.3))  # Host column
        self.table_view.setColumnWidth(3, int(remaining_width * 0.2))  # Database column
        self.table_view.setColumnWidth(4, action_column_width)  # Action column (fixed size)

    def resizeEvent(self, event):
        """Resize table columns when the window is resized."""
        super().resizeEvent(event)
        self.resize_table_columns()

    def filter_table(self):
        """Filter table rows based on the search box input."""
        search_text = self.search_box.text().lower()
        for row in range(self.table_view.rowCount()):
            match = False
            for col in range(self.table_view.columnCount() - 1):  # Exclude the action column
                item = self.table_view.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table_view.setRowHidden(row, not match)

    def open_add_connection_window(self):
        """Open the ConnectionConfig window for creating a new connection."""
        self.connection_config_window = ConnectionConfig(self.ini_file)
        self.connection_config_window.saved.connect(self.load_data)
        self.connection_config_window.show()

    def open_edit_connection_window(self, connection_id):
        """Open the ConnectionConfig window for editing an existing connection."""
        self.connection_config_window = ConnectionConfig(self.ini_file, connection_id)
        self.connection_config_window.saved.connect(self.load_data)
        self.connection_config_window.show()

    def delete_connection(self, connection_id):
        """Delete a connection from the ini file."""
        reply = QMessageBox.question(
            self, 
            'Delete Connection',
            f"Are you sure you want to delete the connection '{connection_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if connection_id in self.config:
                del self.config[connection_id]
                with open(self.ini_file, 'w') as configfile:
                    self.config.write(configfile)
                self.load_data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
