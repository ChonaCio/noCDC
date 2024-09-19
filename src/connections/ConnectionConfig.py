import sys
import configparser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, 
    QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

import subprocess
import importlib
import json
import os

class ConnectionConfig(QMainWindow):
    # Define a signal that will be emitted when the save button is clicked
    saved = pyqtSignal()

    def __init__(self, ini_file, connection_id=None):
        """
        Initialize the ConnectionConfig window.
        If connection_id is None, it means a new connection is being created.
        """
        super().__init__()
        self.setWindowTitle("New Connection" if connection_id is None else f"Connection Details - {connection_id}")
        self.setGeometry(300, 300, 400, 350)  # Adjusted size to accommodate extra fields
        self.ini_file = ini_file
        self.connection_id = connection_id

        # Load the ini file
        self.config = configparser.ConfigParser()
        self.config.read(self.ini_file)

        # Define current directory
        self.curr_dir = os.path.abspath(os.getcwd())

        # Importing definitions defined in JSON
        with open(f'{ self.curr_dir }/src/connections/definitions.json') as json_file:
            self.definitions = json.load(json_file)

        # Templates for different database types with required fields
        self.templates = {}
        template_list = os.listdir(f'{ self.curr_dir }/src/connections/templates')
        for temp in template_list:
            with open(f'{ self.curr_dir }/src/connections/templates/{ temp }') as json_file:
                self.templates[temp.split('.')[0]] = json.load(json_file)
        
        self.default_template = {
            'host': 'db.example.com', 
            'port': '5432', 
            'username': 'user', 
            'password': 'password',
            'database': 'mydatabase'
        }  # Default values

        # Main layout for the window
        self.main_layout = QVBoxLayout()

        # Initialize widgets
        self.id_label = QLabel("Connection ID:")
        self.id_field = QLineEdit(self.connection_id if self.connection_id else '')
        self.id_field.setReadOnly(self.connection_id is not None)  # Unlock ID field if no ID is provided

        self.type_label = QLabel("Type:")
        self.type_dropdown = QComboBox(self)
        
        # Database types, sorted alphabetically

        db_types = sorted([self.definitions[x]['display_name'] for x in self.definitions])
        self.type_dropdown.addItems(db_types)

        # Connect dropdown change to update form with template
        self.type_dropdown.currentTextChanged.connect(self.update_fields_with_template)

        # Initialize fields
        self.host_label = QLabel("Host:")
        self.host_field = QLineEdit()
        
        self.port_label = QLabel("Port:")
        self.port_field = QLineEdit()

        self.username_label = QLabel("Username:")
        self.username_field = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)  # Hide password input

        self.database_label = QLabel("Database:")
        self.database_field = QLineEdit()

        self.schema_label = QLabel("Schema:")
        self.schema_field = QLineEdit()

        # Add widgets to layout
        self.main_layout.addWidget(self.id_label)
        self.main_layout.addWidget(self.id_field)
        self.main_layout.addWidget(self.type_label)
        self.main_layout.addWidget(self.type_dropdown)
        self.main_layout.addWidget(self.host_label)
        self.main_layout.addWidget(self.host_field)
        self.main_layout.addWidget(self.port_label)
        self.main_layout.addWidget(self.port_field)
        self.main_layout.addWidget(self.username_label)
        self.main_layout.addWidget(self.username_field)
        self.main_layout.addWidget(self.password_label)
        self.main_layout.addWidget(self.password_field)
        self.main_layout.addWidget(self.database_label)
        self.main_layout.addWidget(self.database_field)
        self.main_layout.addWidget(self.schema_label)
        self.main_layout.addWidget(self.schema_field)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Add Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)

        # Add Test button
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test_connection)

        # Add Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        # Add buttons to the button layout
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.close_button)

        # Add the button layout to the main layout
        self.main_layout.addLayout(button_layout)

        # Set the layout to the window
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Update fields with the template of the currently selected database type
        self.update_fields_with_template()

        # Preselect the dropdown type and load existing data if editing an existing connection
        if self.connection_id:
            self.load_existing_data()

    def preselect_dropdown_type(self):
        """Pre-select the correct type in the dropdown based on the current value from the ini file."""
        connection_data = self.get_connection_data()
        current_type = connection_data.get('type', '')
        current_type = current_type.lower().replace(" ", "")

        if current_type in self.definitions:
            self.type_dropdown.setCurrentText(self.definitions[current_type]['display_name'])

    def get_connection_data(self):
        """Get the connection details for the given connection ID from the ini file."""
        if self.connection_id in self.config:
            return {
                'type': self.config[self.connection_id].get('type', ''),
                'host': self.config[self.connection_id].get('host', ''),
                'port': self.config[self.connection_id].get('port', ''),
                'username': self.config[self.connection_id].get('username', ''),
                'password': self.config[self.connection_id].get('password', ''),
                'database': self.config[self.connection_id].get('database', ''),
                'schema': self.config[self.connection_id].get('schema', '')
            }
        return {}

    def load_existing_data(self):
        """Load existing data from the ini file into the form fields."""
        connection_data = self.get_connection_data()
        if connection_data:
            self.preselect_dropdown_type()
            self.host_field.setText(connection_data.get('host', ''))
            self.port_field.setText(connection_data.get('port', ''))
            self.username_field.setText(connection_data.get('username', ''))
            self.password_field.setText(connection_data.get('password', ''))
            self.database_field.setText(connection_data.get('database', ''))
            self.schema_field.setText(connection_data.get('schema', ''))
        self.update_fields_with_template()

    def update_fields_with_template(self):
        """Update the form fields based on the selected database type."""
        selected_type = self.type_dropdown.currentText().lower().replace(" ", "")
        template = self.templates.get(selected_type, self.default_template)

        # Update the placeholder text for fields based on the selected template
        self.host_field.setPlaceholderText(template['host'])
        self.port_field.setPlaceholderText(template['port'])
        self.username_field.setPlaceholderText(template['username'])
        self.password_field.setPlaceholderText(template['password'])
        self.database_field.setPlaceholderText(template['database'])
        
        # Update visibility of fields based on the selected database type
        if selected_type == 'snowflake':
            self.schema_label.setVisible(True)
            self.schema_field.setVisible(True)
            self.schema_field.setPlaceholderText(template.get('schema', ''))
        else:
            self.schema_label.setVisible(False)
            self.schema_field.setVisible(False)

    def validate_fields(self):
        """Validate that all required fields are filled."""
        if not self.host_field.text() or not self.port_field.text() or not self.username_field.text() or \
           not self.password_field.text() or not self.database_field.text():
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields.")
            return False
        if self.schema_field.isVisible() and not self.schema_field.text():
            QMessageBox.warning(self, "Validation Error", "Please fill in the schema field.")
            return False
        return True

    def save_changes(self):
        """Save the changes to the ini file."""
        if not self.validate_fields():
            return
        
        selected_type = self.type_dropdown.currentText()
        new_type = selected_type.lower().replace(" ", "")
        new_host = self.host_field.text()
        new_port = self.port_field.text()
        new_username = self.username_field.text()
        new_password = self.password_field.text()
        new_database = self.database_field.text()
        new_schema = self.schema_field.text() if self.schema_field.isVisible() else ''

        # Check if creating a new connection
        if not self.connection_id:
            # Generate a new unique connection ID
            self.connection_id = f"connection_{len(self.config.sections()) + 1}"
            self.config[self.connection_id] = {}

        # Update the ini file with the new data
        self.config[self.connection_id]['type'] = new_type
        self.config[self.connection_id]['host'] = new_host
        self.config[self.connection_id]['port'] = new_port
        self.config[self.connection_id]['username'] = new_username
        self.config[self.connection_id]['password'] = new_password
        self.config[self.connection_id]['database'] = new_database
        if new_schema:
            self.config[self.connection_id]['schema'] = new_schema

        # Write the updated config back to the file
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)

        # Emit the saved signal
        self.saved.emit()

        # Display a message box confirming the save
        QMessageBox.information(self, "Saved", f"Connection '{self.connection_id}' has been saved.")
        self.close()

    def check_and_install_packages(self, db_type):
        """Check if required packages are installed, and prompt for installation if missing."""

        missing_packages = []
        for package in self.definitions[db_type]['dependencies']:
            if importlib.util.find_spec(package) is None:
                missing_packages.append(package)

        if missing_packages:
            reply = QMessageBox.question(
                self, 
                "Missing Packages",
                f"The following packages are required but not installed:\n{', '.join(missing_packages)}\n"
                f"Do you want to install them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                for package in missing_packages:
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    except subprocess.CalledProcessError:
                        QMessageBox.critical(self, "Installation Failed", f"Failed to install {package}. Please install it manually.")
                        return False
                return True
            else:
                return False
        return True

    def test_connection(self):
        """Test the connection using SQLAlchemy."""
        if not self.validate_fields():
            return
        
        selected_type = self.type_dropdown.currentText().lower().replace(" ", "")

        # Check and install missing packages if necessary
        if not self.check_and_install_packages(selected_type):
            return  # Abort the test if the user declines installation

        host = self.host_field.text()
        port = self.port_field.text()
        username = self.username_field.text()
        password = self.password_field.text()
        database = self.database_field.text()
        schema = self.schema_field.text() if self.schema_field.isVisible() else ''

        connection_string = self.definitions[selected_type]['connection_string'].format(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            schema=schema
        )
        
        try:
            # Create a SQLAlchemy engine
            engine = create_engine(connection_string)
            # Test the connection by connecting to the database
            with engine.connect() as connection:
                QMessageBox.information(self, "Connection Test", "Connection successful!")
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Connection Test Failed", f"Failed to connect: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConnectionConfig("data/connections.ini", None)  # Open with blank fields
    window.show()
    sys.exit(app.exec())
