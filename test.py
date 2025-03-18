import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolButton, QButtonGroup
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np


class CustomToolbar(NavigationToolbar):
    """Custom Matplotlib Toolbar with Two Toggle Buttons (Can Be Unchecked)"""
    def __init__(self, canvas, ax, parent=None):
        super().__init__(canvas, parent)

        self.ax = ax  # Store reference to axes

        # Create Toggle Buttons
        self.grid_button = QToolButton(self)
        self.grid_button.setCheckable(True)
        self.grid_button.setIcon(QIcon("grid_icon.png"))  # Replace with your image
        self.grid_button.setToolTip("Toggle Grid")
        self.grid_button.clicked.connect(self.toggle_grid)

        self.dark_mode_button = QToolButton(self)
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.setIcon(QIcon("dark_mode_icon.png"))  # Replace with your image
        self.dark_mode_button.setToolTip("Toggle Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Button Group (Allow Manual Unchecking)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(False)  # Allows unchecking
        self.button_group.addButton(self.grid_button)
        self.button_group.addButton(self.dark_mode_button)

        # Insert buttons on the LEFT side of the toolbar
        self.insertWidget(self.actions()[0], self.grid_button)
        self.insertWidget(self.actions()[0], self.dark_mode_button)

    def toggle_grid(self):
        """Toggle the grid ON/OFF"""
        if self.grid_button.isChecked():
            self.ax.grid(True)  # Enable grid
            self.dark_mode_button.setChecked(False)  # Turn off dark mode

        else:
            self.ax.grid(False)  # Disable grid
        self.ax.figure.canvas.draw()

    def toggle_dark_mode(self):
        """Toggle dark mode ON/OFF"""
        if self.dark_mode_button.isChecked():
            self.ax.set_facecolor("#333333")  # Dark background
            self.grid_button.setChecked(False)  # Turn off grid
        else:
            self.ax.set_facecolor("white")  # Reset background color
        self.ax.figure.canvas.draw()


class MatplotlibWidget(QWidget):
    """Main widget containing the Matplotlib figure and custom toolbar"""
    def __init__(self):
        super().__init__()

        # Create figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Custom Matplotlib toolbar (pass ax reference)
        self.toolbar = CustomToolbar(self.canvas, self.ax, self)

        # Example plot
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.ax.plot(x, y, label="Sine Wave")
        self.ax.legend()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main PyQt Application Window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toggle Buttons in Matplotlib Toolbar")

        # Set main widget
        self.matplotlib_widget = MatplotlibWidget()
        self.setCentralWidget(self.matplotlib_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
