import sys
from PySide6.QtWidgets import QToolButton,QVBoxLayout,QLabel,QComboBox,QPushButton, QDialog,QApplication,QDialogButtonBox,QHBoxLayout,QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from tkinter import messagebox
from qtpy.QtCore import Qt

from matplotlib.legend import Legend
from matplotlib.patches import Patch


from superqt import QRangeSlider













class CustomQRangeSlider(QRangeSlider):
    """Custom QRangeSlider that emits a signal when the slider is released."""
    
    sliderReleased = Signal(tuple)  # Define a custom signal that sends the slider values

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        """Initialize with the specified orientation (default: Horizontal)."""
        super().__init__(orientation, parent)  # Pass orientation to the parent class

    def mouseReleaseEvent(self, event):
        """Detects when the user releases the slider and emits the custom signal."""
        super().mouseReleaseEvent(event)  # Call the default behavior
        self.sliderReleased.emit(self.value())  # Emit signal with the current values



class CustomWidgetRangeSlider(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.wavelenghts = [i for i in range(10)]
        layout = QHBoxLayout(self)
        

        self.wl_min_label = QLabel() 
        layout.addWidget(self.wl_min_label)
        self.range_slider = CustomQRangeSlider()
        layout.addWidget(self.range_slider)
        self.wl_max_label = QLabel() 
        layout.addWidget(self.wl_max_label)

        self.setRange(self.wavelenghts)
        self.update_label((0,len(self.wavelenghts)-1))
        self.range_slider.setValue((0,len(self.wavelenghts)-1))


        self.range_slider.valueChanged.connect(self.update_label)

    def update_label(self, value):
        """Update labels and restrict slider movement to allowed values."""
        
        min_index, max_index = value  # Get slider positions
        min_value, max_value = int(self.wavelenghts[min_index]), int(self.wavelenghts[max_index])  # Map indices to values
        self.wl_min_label.setText("{}".format(min_value))
        self.wl_max_label.setText("{}".format(max_value))
        """Reduit l'étude des clustering aux valeurs indiqués"""

    def setRange(self, wavelenghts):
        if wavelenghts:
            self.range_slider.setRange(0,len(wavelenghts)-1)
        else :
            print("WARNING : wavelenght is None in CustomWidgetRangeSlider.setRange(",wavelenghts ,")")
            self.range_slider.setRange(0,10)

    def setWavelenghts(self,wavelenghts):
        self.wavelenghts = wavelenghts
        self.setRange(self.wavelenghts) #update the range
        self.range_slider.setValue((0,len(wavelenghts)-1))
