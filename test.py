from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Signal
from superqt import QRangeSlider

class CustomQRangeSlider(QRangeSlider):
    """Custom QRangeSlider that emits a signal when the slider is released."""
    
    sliderReleased = Signal(tuple)  # Define a custom signal that sends the slider values

    def mouseReleaseEvent(self, event):
        """Detects when the user releases the slider and emits the custom signal."""
        super().mouseReleaseEvent(event)  # Call the default behavior
        self.sliderReleased.emit(self.value())  # Emit signal with the current values

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom QRangeSlider with sliderReleased Signal")

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create a Custom QRangeSlider
        self.slider = CustomQRangeSlider()
        self.slider.setRange(0, 100)  # Set min & max values
        self.slider.setValue((20, 80))  # Set initial range

        # Label to show the released range
        self.label = QLabel(f"Released Range: {self.slider.value()}")

        # Connect the custom signal to update the label
        self.slider.sliderReleased.connect(self.on_slider_released)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setCentralWidget(central_widget)

    def on_slider_released(self, value):
        """Update the label when the slider is released."""
        self.label.setText(f"Released Range: {value}")
        print(f"Slider released at: {value}")  # Debugging output

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
