import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QHBoxLayout, QPushButton
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

        # Horizontal and Vertical Sliders
        self.h_slider = QSlider(Qt.Vertical, self)
        self.h_slider.setRange(0, screen_size.height())
        self.h_slider.setValue(screen_size.height() // 2)  # Set to center
        self.h_slider.valueChanged.connect(self.update)
        self.v_slider = QSlider(Qt.Horizontal, self)
        self.v_slider.setRange(0, screen_size.width())
        self.v_slider.setValue(screen_size.width() // 2)  # Set to center
        self.v_slider.valueChanged.connect(self.update)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(QApplication.quit)

        layout = QVBoxLayout()
        layout.addWidget(self.v_slider)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.h_slider)
        h_layout.addStretch()
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
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawLine(self.v_slider.value(), 0, self.v_slider.value(), self.height())

        inverted_h_value = self.height() - self.h_slider.value()
        painter.drawLine(0, inverted_h_value, self.width(), inverted_h_value)


        painter.end()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

def manage_gif():
    try:
        gif_process = subprocess.Popen(["python", "griddy_gif.py"])
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
