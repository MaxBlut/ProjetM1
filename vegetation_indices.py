import sys
import random
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
import re

from utiles import closest_id

from CustomElement import CustomCanvas,hyperspectral_appli

from math import sqrt
sqrt(0)
class veget_indices(hyperspectral_appli):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Plotter")
        self.variable_init()
        self.init_ui()

    def variable_init(self):
        self.original_wavelengths = None    # liste de toutes les longueurs d'ondes enregistré par la cam
        self.wl_min_cursor = None       # l'indice de longueur d'onde min du slider
        self.wl_max_cursor = None       # l'indice de longueur d'onde max du slider
        self.data_img = None
        self.file_path = None

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #  Remove existing layout if there is one
        if central_widget.layout() is not None:
            old_layout = central_widget.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            old_layout.deleteLater()
        # Layout
        layout = QVBoxLayout(central_widget)

        # Dropdown menu (ComboBox)
        self.dropdown = QComboBox()
        layout.addWidget(self.dropdown)

        # Button to load file
        self.load_button = QPushButton("Load File")
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.process_equation)
        layout.addWidget(self.plot_button)
        


        # Matplotlib Figure and Canvas
        self.figure, self.axs = plt.subplots(1, 2, figsize=(5, 5))
        self.axs[1] = self.figure.add_subplot(1, 2, 2, projection='3d')
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.canvas = FigureCanvas(self.figure)

        
        layout.addWidget(self.canvas)

        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)
        self.populate_drop_down()

        # Connect mouse movement event
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


    def populate_drop_down(self):
        """Reads the file, populates the dropdown, and adds tooltips."""
        file_path = "equations.txt"
        if file_path:
            self.dropdown.clear()  # Clear previous options
            with open(file_path, "r") as file:
                for line in file:
                    # Split each line into name and equation
                    parts = line.strip().split(":", 1)  # Split by the first colon
                    if len(parts) == 2:
                        name, equation = parts[0].strip(), parts[1].strip()
                        self.dropdown.addItem(name)  # Show only the name
                        self.dropdown.setItemData(self.dropdown.count() - 1, equation)  # Store equation as tooltip


    def on_mouse_move(self, event):
        if event.button == 2:  # Left mouse button
            self.axs[1].view_init(elev=self.axs[1].elev , azim=self.axs[1].azim)  # Keep elevation fixed  elev=35,
            self.figure.canvas.draw_idle()  # Update plot


    def process_equation(self):
        """
        Process the given equation to extract and compute values from hyperspectral data.

        Parameters:
        - equation (str): The equation string (e.g., "(R2000 + R2200) / 2").
        - hyperspectral_data (numpy.ndarray): 3D array with shape (height, width, bands).
        - wavelengths (list): List of wavelengths corresponding to bands in hyperspectral_data.

        Returns:
        - numpy.ndarray: The computed 2D array result of the equation.
        """
        # equation = self.dropdown.currentText()
        selected_index = self.dropdown.currentIndex()  # Get selected index
        equation = self.dropdown.itemData(selected_index)
        print(equation)
        # Extract wavelength values from the equation
        found_wavelengths = re.findall(r'R(\d+)', equation)
        
        # Create a dictionary that maps RXXXX to the correct band in hyperspectral data
        local_dict = {}
        if len(found_wavelengths)==0:
            print("wl not found in the equation text")
            return -2
        self.axs[0].clear() 
        self.axs[1].clear() 
        for wl in found_wavelengths:
            wl = int(wl)
            band_index = closest_id(wl,self.original_wavelengths,accuracy=2)
            if band_index is None:
                print("wl value not found")
                return -1
            data = self.data_img[:,:,band_index]
            local_dict[f'R{int(wl)}'] = np.squeeze(data)
        # Evaluate the equation safely
        
        try:
            result = eval(equation, {"__builtins__": {}}, local_dict)
        except Exception as e:
            raise ValueError(f"Error evaluating equation: {e}")
        self.axs[0].imshow(result,cmap='nipy_spectral')
        X ,Y = np.linspace(0,result.shape[1],result.shape[1]),np.linspace(0,-result.shape[0], result.shape[0])
        X, Y = np.meshgrid(X,Y)
        # print(X.shape)
        # print(Y.shape)
        self.axs[1].plot_surface(X,Y,result, cmap='nipy_spectral')
        self.canvas.draw()
        return 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = veget_indices()
    window.show()
    sys.exit(app.exec())
