import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QLabel, QDialog, QCheckBox, QSpinBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QScreen

class RulerOverlay(QWidget):
    def __init__(self):
        super().__init__()

        screen: QScreen = QApplication.primaryScreen()
        screen_size = screen.size()

        self.setWindowTitle('Ruler Overlay')
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        self.setWindowOpacity(0.5)  # Set transparency
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Default values
        self.grid_size = 40  # Default to 50 pixels
        self.line_color = QColor(0, 255, 0)  # Default to green

        # Horizontal and Vertical Sliders
        self.h_slider = QSlider(Qt.Vertical, self)
        self.h_slider.setRange(0, screen_size.height())
        self.h_slider.setValue(screen_size.height() // 2)  # Set to center
        self.h_slider.valueChanged.connect(self.update)
        self.v_slider = QSlider(Qt.Horizontal, self)
        self.v_slider.setRange(0, screen_size.width())
        self.v_slider.setValue(screen_size.width() // 2)  # Set to center
        self.v_slider.valueChanged.connect(self.update)

        # Options Button
        self.options_button = QPushButton("Options", self)
        self.options_button.clicked.connect(self.show_options_dialog)
        self.is_grid_enabled = False
        
        # Color Picker
        self.color_button = QPushButton("Pick Color", self)
        self.color_button.clicked.connect(self.pick_color)

        # Exit Button
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(QApplication.quit)

        layout = QVBoxLayout()
        layout.addWidget(self.v_slider)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.h_slider)
        h_layout.addStretch()
        h_layout.addWidget(self.options_button)
        h_layout.addWidget(self.color_button)
        h_layout.addWidget(self.exit_button) 

        layout.addLayout(h_layout)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw horizontal ruler markings
        for i in range(0, self.width(), 10):
            if i % 50 == 0:
                painter.drawLine(i, 0, i, 20)
            else:
                painter.drawLine(i, 0, i, 10)

        # Draw vertical ruler markings
        for i in range(0, self.height(), 10):
            if i % 50 == 0:
                painter.drawLine(0, i, 20, i)
            else:
                painter.drawLine(0, i, 10, i)

        # Calculate slider handle positions
        v_ratio = self.v_slider.value() / self.v_slider.maximum()
        v_handle_x = int(v_ratio * self.v_slider.width())

        # Draw draggable lines
        painter.setPen(QPen(self.line_color, 2))
        painter.drawLine(self.v_slider.value(), 0, self.v_slider.value(), self.height())

        inverted_h_value = self.height() - self.h_slider.value()
        painter.drawLine(0, inverted_h_value, self.width(), inverted_h_value)

        if self.is_grid_enabled:
            for i in range(0, self.width(), self.grid_size):  # Assuming a grid spacing of 50 pixels
                painter.drawLine(i, 0, i, self.height())
            for j in range(0, self.height(), self.grid_size):
                painter.drawLine(0, j, self.width(), j)

        painter.end()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def pick_color(self):
        try:
            color_dialog = QColorDialog(self)
            if color_dialog.exec_() == QColorDialog.Accepted:
                self.line_color = color_dialog.selectedColor()
                self.update()  # Force a repaint
        except Exception as e:
            print(f"Exception encountered: {e}")

    def show_options_dialog(self):
        dialog = OptionsDialog(self)
        dialog.exec_()

    def enable_grid(self):
        self.is_grid_enabled = True
        self.update()  # To trigger a repaint

    def disable_grid(self):
        self.is_grid_enabled = False
        self.update()

# End RulerOverlay class

# OptionsDialog Class
class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.resize(300, 200)

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

        self.grid_size_spinbox = QSpinBox(self)
        self.grid_size_spinbox.setRange(10, 200)
        self.grid_size_spinbox.setValue(parent.grid_size)
        self.grid_size_spinbox.setSuffix(" px")
        self.grid_size_spinbox.valueChanged.connect(self.grid_size_changed)

        # Apply Changes button
        self.apply_button = QPushButton("Apply Changes", self)
        self.apply_button.clicked.connect(self.apply_changes)

        # Add grid-related options to the layout
        grid_layout = QVBoxLayout()
        grid_layout.addWidget(self.grid_checkbox)
        grid_layout.addWidget(self.grid_size_spinbox)

        # Add widgets to the main layout
        self.layout.addWidget(self.opacity_label)
        self.layout.addWidget(self.opacity_slider)
        self.layout.addLayout(grid_layout)
        self.layout.addWidget(self.apply_button)

        # Set the main layout for the dialog
        self.setLayout(self.layout)

    def adjust_opacity(self, value):
        opacity = 0.10 + (value / 100) * 0.9  # Min value of 10% to prevent invisible menu
        self.parent().setWindowOpacity(opacity)
        self.opacity_label.setText(f"Opacity: {int(opacity*100)}%")

    def grid_size_changed(self):
        self.parent().grid_size = self.grid_size_spinbox.value()
        if self.grid_checkbox.isChecked():
            self.parent().enable_grid()

    def apply_changes(self):
        if self.grid_checkbox.isChecked():
            self.parent().enable_grid()
        else:
            self.parent().disable_grid()
        self.accept()  # Close the dialog if using QDialog

def manage_gif():
    try:
        gif_process = subprocess.Popen(["python", "./src/griddy_gif.py"])
        return gif_process
    except:
        return None

if __name__ == '__main__':
    gif_process = manage_gif()
    app = QApplication(sys.argv)
    window = RulerOverlay()
    window.show()
    app.exec_()

    # Terminate the gif subprocess when the QApplication exits if it is still open
    if gif_process:
        gif_process.terminate()
