import sys
import random
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
from numpy import sqrt
import re

from utiles import closest_id

from CustomElement import CustomCanvas,hyperspectral_appli





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
        self.high_res = None
        self.low_res = None

    def init_ui(self):
        
        # Layout
        layout = QVBoxLayout()

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
        self.axs[1].axis('off')
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

        # Connect events
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_mouse_drag)
        self.figure.canvas.mpl_connect("button_release_event", self.on_mouse_release)

       

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


    


    def process_equation(self):
        """
        Process the given equation to extract and compute values from hyperspectral data.

        Parameters:
        - equation (str): The equation string (e.g., "(R2000 + R2200) / 2").
        - hyperspectral_data (numpy.ndarray): 3D array with shape (height, width, bands).
        - wavelengths (list): List of wavelengths corresponding to bands in hyperspectral_data.

        
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
        local_dict['sqrt'] = sqrt
        local_dict['abs'] = abs
        try:
            result = eval(equation, {"__builtins__": {}} , local_dict) 
        except Exception as e:
            raise ValueError(f"Error evaluating equation: {e}")
        self.axs[0].imshow(result,cmap='nipy_spectral')
        X ,Y = np.linspace(0,result.shape[1],result.shape[1]),np.linspace(0,-result.shape[0], result.shape[0])
        X, Y = np.meshgrid(X,Y)
        # print(X.shape)
        # print(Y.shape)
        self.high_res = self.axs[1].plot_surface(X,Y,result, cmap='nipy_spectral')
        self.low_res = self.axs[1].plot_wireframe(X[::50, ::50],Y[::50, ::50],result[::50,::50], cmap='nipy_spectral',alpha=0.5)
        self.low_res.set_visible(False)
        self.canvas.draw()
        return 
    

    def on_mouse_move(self, event):
        if event.button == 1:  # Left mouse button
            self.axs[1].view_init(elev=self.axs[1].elev , azim=self.axs[1].azim,roll=0)  # Keep elevation fixed  elev=35,
            self.figure.canvas.draw_idle()  # Update plot


    def on_mouse_drag(self, event):
        """ While rotating, show the low-resolution version. """
        
        if event.button == 1 and self.high_res and self.low_res:  # Left mouse button
            self.high_res.set_visible(False)  # Hide heavy plot
            self.low_res.set_visible(True)  # Show low-poly version
            self.figure.canvas.draw_idle()  # Refresh plot faster


    def on_mouse_release(self,event):
        """ When releasing the mouse, restore full quality. """
        if self.high_res and self.low_res:
            self.high_res.set_visible(True)  # Show high-res plot
            self.low_res.set_visible(False)  # Hide low-res plot
            self.figure.canvas.draw_idle()  # Refresh plot





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = veget_indices()
    window.show()
    sys.exit(app.exec())
