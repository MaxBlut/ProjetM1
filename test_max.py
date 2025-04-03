from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal
import sys

class CustomWidget(QWidget):
    def __init__(self, resize_signal, parent=None):
        super().__init__(parent)

        # Connect the resize signal from QMainWindow
        resize_signal.connect(self.handle_resize)

        # Create a label to show the window size
        self.label = QLabel("Window Size: Unknown", self)

        # Layout to organize widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def handle_resize(self, width, height):
        """ Update the label when the window resizes """
        self.label.setText(f"Window Size: {width}x{height}")
        print(f"CustomWidget detected resize: {width}x{height}")

class MyWindow(QMainWindow):
    # Define a signal that emits new width & height
    resized = Signal(int, int)

    def __init__(self):
        super().__init__()

        # Create an instance of CustomWidget and pass the resize signal
        self.widget = CustomWidget(self.resized)
        self.setCentralWidget(self.widget)

        self.setWindowTitle("Pass Resize Signal Example")
        self.resize(800, 600)  # Initial size

    def resizeEvent(self, event):
        """ Emits the signal when the window is resized """
        width, height = event.size().width(), event.size().height()
        self.resized.emit(width, height)  # Emit signal with new size
        super().resizeEvent(event)

# Run the application
app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec_())
