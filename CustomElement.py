import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolButton, QButtonGroup
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.legend import Legend

class CustomToolbar(NavigationToolbar):
    """Custom Matplotlib Toolbar with Two Toggle Buttons (Can Be Unchecked)"""
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.parent = parent
        # Create Toggle Buttons
        self.mean_spctr_point_button = QToolButton(self)
        self.mean_spctr_point_button.setCheckable(True)
        self.mean_spctr_point_button.setIcon(QIcon("i-remade-that-hamster-meme-into-my-rat-v0-cercyjvmn3kb1.jpg"))  # Replace with your image
        self.mean_spctr_point_button.setToolTip("plot_mean_spctr_point")
        # self.mean_spctr_point_button.clicked.connect(self.plot_mean_spctr_point())
        """
        self.dark_mode_button = QToolButton(self)
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.setIcon(QIcon("dark_mode_icon.png"))  # Replace with your image
        self.dark_mode_button.setToolTip("Toggle Dark Mode")
        # self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        """
        # Button Group (Allow Manual Unchecking)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(False)  # Allows unchecking
        self.button_group.addButton(self.mean_spctr_point_button)
        # self.button_group.addButton(self.dark_mode_button)

        # Insert buttons on the LEFT side of the toolbar
        self.insertWidget(self.actions()[0], self.mean_spctr_point_button)
        # self.insertWidget(self.actions()[0], self.dark_mode_button)

        self.canvas.mpl_connect("button_press_event",self.on_click)


    def on_click(self, event):
        # Handle mouse click events.
        if self.mean_spctr_point_button.isChecked():
            if self.parent.data_img is not None:
                if event.inaxes == self.parent.axs[0]:  # Check if click is on the left graph
                    if event.xdata is not None and event.ydata is not None:
                        
                        x, y = int(event.xdata), int(event.ydata)
                        data = self.parent.data_img[y,x,:].reshape(1,-1)
                        line, = self.parent.axs[1].plot(self.parent.wavelengths, data[0] , label=f"Point ({x}, {y})")

                        self.parent.legend_obj.remove()  # Remove the previous legend
                        self.parent.legend_label.append(f"Point ({x}, {y})")
                        legend = PickableLegend(self.parent.axs[1], self.parent.axs[1].get_lines(), self.parent.legend_label)
                        self.parent.legend_obj = self.parent.axs[1].add_artist(legend)
                        # on récupere la ligne n°-1 (la derniere) de la légende du graphique de droite
                        
                        self.parent.canvas.draw()  # Update the figure




class PickableLegend(Legend):
    """Custom Legend that enables picking on legend items by default."""
    # Store the original legend lines and their corresponding plot lines
    def __init__(self, parent_ax, *args, **kwargs):
        super().__init__(parent_ax, *args, **kwargs)
        self.parent_ax = parent_ax  # Store reference to the axes

        # Enable picking for all legend items
        self._enable_picking()

    def _enable_picking(self):
        """Enable picking for all legend lines."""
        for leg_line, orig_line in zip(self.get_lines(), self.parent_ax.get_lines()):
            leg_line.set_picker(True)  # Enable clicking on legend items
            leg_line.set_pickradius(8)  # Make it easier to click
            leg_line.original_line = orig_line  # Store reference to the plot line
        











class MatplotlibWidget(QWidget):
    """Main widget containing the Matplotlib figure and custom toolbar"""
    def __init__(self):
        super().__init__()

        # Create figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Custom Matplotlib toolbar (pass ax reference)
        self.toolbar = CustomToolbar(self.canvas, self)

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
