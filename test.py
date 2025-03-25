from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from superqt import QRangeSlider
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QRangeSlider with Labels & Value Restriction")

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Allowed values for the slider (custom steps)
        self.allowed_values = np.array([402, 420, 450, 500, 600, 700, 800, 900, 998])

        # Create a QRangeSlider
        self.slider = QRangeSlider()
        self.slider.setRange(0, len(self.allowed_values) - 1)  # Slider moves in index positions
        self.slider.setValue((0, len(self.allowed_values) - 1))  # Default to min & max index

        # Labels to show the current values
        self.label = QLabel("Range: {} - {}".format(self.allowed_values[0], self.allowed_values[-1]))

        # Connect slider change event
        self.slider.valueChanged.connect(self.update_labels)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setCentralWidget(central_widget)

    def update_labels(self, value):
        """Update labels and restrict slider movement to allowed values."""
        min_index, max_index = value  # Get slider positions
        min_value, max_value = self.allowed_values[min_index], self.allowed_values[max_index]  # Map indices to values
        self.label.setText(f"Range: {min_value} - {max_value}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
