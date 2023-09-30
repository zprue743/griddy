import os
import configparser
from PyQt5.QtWidgets import QSlider, QVBoxLayout, QPushButton, QLabel, QDialog, QCheckBox, QSpinBox, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.resize(300, 350)

        # Config path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, "config", "config.ini")

        # Main layout for the dialog
        self.layout = QVBoxLayout()

        # Opacity Slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(parent.windowOpacity() * 100))
        self.opacity_slider.valueChanged.connect(self.adjust_opacity)
        self.opacity_label = QLabel(f"Opacity: {self.opacity_slider.value()}%")

        # Grid option
        self.grid_checkbox = QCheckBox("Show Grid Overlay", self)
        self.grid_checkbox.setChecked(parent.is_grid_enabled)
        self.grid_checkbox.stateChanged.connect(self.grid_state_changed)

        self.grid_size_spinbox = QSpinBox(self)
        self.grid_size_spinbox.setRange(10, 200)
        self.grid_size_spinbox.setValue(parent.grid_size)
        self.grid_size_spinbox.setSuffix(" px")
        self.grid_size_spinbox.valueChanged.connect(self.grid_size_changed)

        # Save Config button
        self.save_config_button = QPushButton("Save Config", self)
        self.save_config_button.clicked.connect(self.save_config)

        # Load Config button
        self.load_config_button = QPushButton("Load Config", self)
        self.load_config_button.clicked.connect(self.load_config)

        # Reset Config Button
        self.reset_config_button = QPushButton("Reset Config", self)
        self.reset_config_button.clicked.connect(self.reset_config)

        # Color Picker button
        self.color_button = QPushButton("Pick Color", self)
        self.color_button.clicked.connect(self.pick_color)

        # Add grid-related options to the layout
        grid_layout = QVBoxLayout()
        grid_layout.addWidget(self.grid_checkbox)
        grid_layout.addWidget(self.grid_size_spinbox)

        # Add widgets to the main layout
        self.layout.addWidget(self.opacity_label)
        self.layout.addWidget(self.opacity_slider)
        self.layout.addLayout(grid_layout)
        self.layout.addWidget(self.save_config_button)
        self.layout.addWidget(self.load_config_button)
        self.layout.addWidget(self.reset_config_button)

        # Set the main layout for the dialog
        self.setLayout(self.layout)

    def adjust_opacity(self, value):
        opacity = 0.10 + (value / 100) * 0.9  # Min value of 10% to prevent invisible menu
        self.parent().setWindowOpacity(opacity)
        self.opacity_label.setText(f"Opacity: {int(opacity*100)}%")

    def grid_size_changed(self):
        self.parent().grid_size = self.grid_size_spinbox.value()
        if self.grid_checkbox.isChecked():
            self.enable_grid()

    def save_config(self):
        try:
            if not os.path.exists(self.config_path):
                self.create_config_file()

            config = configparser.ConfigParser()
            config.read(self.config_path)

            # Update the values in the existing "Settings" section or create a new one
            if 'Settings' not in config:
                config['Settings'] = {}

            config['Settings']['Opacity'] = str(self.opacity_slider.value())
            config['Settings']['Grid_Enabled'] = str(int(self.grid_checkbox.isChecked()))
            config['Settings']['Grid_Size'] = str(self.grid_size_spinbox.value())
            config['Settings']['Line_Color'] = str(self.parent().line_color.getRgb())

            with open(self.config_path, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f'An error occurred while saving the config file: {e}')

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                self.create_config_file()
            config = configparser.ConfigParser()
            config.read(self.config_path)

            self.opacity_slider.setValue(config.getint('Settings', 'opacity'))
            self.grid_checkbox.setChecked(config.getboolean('Settings', 'grid_enabled'))
            self.grid_size_spinbox.setValue(config.getint('Settings', 'grid_size'))
            line_color_values = tuple(map(int, config.get('Settings', 'line_color').strip('() ').split(',')))
            line_color = QColor(*line_color_values)
            self.parent().line_color = line_color
            self.update_main_window()

        except Exception as e:
            print(f'An error occurred while loading the config file: {e}')

    def reset_config(self):
        try:
            if not os.path.exists(self.config_path):
                self.create_config_file()
            config = configparser.ConfigParser()
            config.read(self.config_path)

            self.opacity_slider.setValue(config.getint('Default', 'opacity'))
            self.grid_checkbox.setChecked(config.getboolean('Default', 'grid_enabled'))
            self.grid_size_spinbox.setValue(config.getint('Default', 'grid_size'))
            line_color_values = tuple(map(int, config.get('Default', 'line_color').strip('() ').split(',')))
            line_color = QColor(*line_color_values)
            self.parent().line_color = line_color
            self.update_main_window()
        
        except Exception as e:
            print(f'An error occurred while resetting the config: {e}')

    def pick_color(self):
        try:
            color_dialog = QColorDialog(self)
            if color_dialog.exec_() == QColorDialog.Accepted:
                self.parent().line_color = color_dialog.selectedColor()
                self.update_main_window()
        except Exception as e:
            print(f"Exception encountered: {e}")

    def enable_grid(self):
        self.parent().is_grid_enabled = True
        self.update_main_window()  # To trigger a repaint

    def disable_grid(self):
        self.parent().is_grid_enabled = False
        self.update_main_window()

    def create_config_file(self):
        os.mkdir(os.path.split(self.config_path)[0])
        config = configparser.ConfigParser()

        config['Settings'] = {}
        config['Default'] = {}

        config['Settings']['Opacity'] = '50'
        config['Settings']['Grid_Enabled'] = '0'
        config['Settings']['Grid_Size'] = '40'
        config['Settings']['Line_Color'] = '(0, 255, 0, 255)'

        config['Default']['Opacity'] = '50'
        config['Default']['Grid_Enabled'] = '0'
        config['Default']['Grid_Size'] = '40'
        config['Default']['Line_Color'] = '(0, 255, 0, 255)'

        with open(self.config_path, 'w') as configfile:
                config.write(configfile)

    def grid_state_changed(self, state):
        if state == Qt.Checked:
            self.enable_grid()
        else:
            self.disable_grid()
        self.update_main_window()

    def update_main_window(self):
        self.parent().update()