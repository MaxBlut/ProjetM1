import sys
import random
import spectral as sp
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog,QHBoxLayout,QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
from numpy import sqrt

import re

from utiles import closest_id, custom_clear

from PySide6.QtCore import Signal, Qt

from vispy import scene
from vispy.scene import visuals, transforms


class veget_indices(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Dropdown Plotter")
        self.variable_init()
        self.init_ui()

    def variable_init(self):
        self.wavelengths = None    # liste de toutes les longueurs d'ondes enregistré par la cam
        self.wl_min_cursor = None       # l'indice de longueur d'onde min du slider
        self.wl_max_cursor = None       # l'indice de longueur d'onde max du slider
        self.data_img = None
        self.file_path = None
        self.high_res = None
        self.low_res = None

    def init_ui(self):
        
        # Layouts
        layout = QVBoxLayout()
        figure_layout = QHBoxLayout()

        # Dropdown menu (ComboBox)
        self.dropdown = QComboBox()
        layout.addWidget(self.dropdown)

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.process_equation)
        layout.addWidget(self.plot_button)
     
        # Matplotlib Figure and Canvas
        self.axs=[None]
        self.figure, self.axs[0] = plt.subplots(1, 1, figsize=(5, 5))
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.canvas = FigureCanvas(self.figure)
        figure_layout.addWidget(self.canvas)

        # Create a VisPy canvas (GPU-rendered)
        self.SceneCanvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
        figure_layout.addWidget(self.SceneCanvas.native)
        layout.addLayout(figure_layout)

        # Create a 3D view
        self.view = self.SceneCanvas.central_widget.add_view()
        self.view.camera = 'turntable'  # Interactive 3D rotation
        self.view.camera.scale_factor = 600

        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.populate_drop_down()
        
        self.setLayout(layout)
        # Connect mouse movement event
        self.SceneCanvas.events.mouse_press.connect(self.on_mouse_click)

       

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
        # print(equation)
        # Extract wavelength values from the equation
        found_wavelengths = re.findall(r'R(\d+)', equation)
        
        # Create a dictionary that maps RXXXX to the correct band in hyperspectral data
        local_dict = {}
        if len(found_wavelengths)==0:
            print("wl not found in the equation text")
            return -2
        self.axs[0].clear() 
        for wl in found_wavelengths:
            wl = int(wl)
            band_index = closest_id(wl,self.wavelengths,accuracy=2)
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
        self.plot_3D(result)
        return 
    

    def plot_3D(self, result):
        X ,Y = np.linspace(0,result.shape[1],result.shape[1]),np.linspace(0,-result.shape[0], result.shape[0])
        X, Y = np.meshgrid(X,Y)
        X_flat, Y_flat, Z_flat = X.flatten(), Y.flatten(), result.flatten()

        # Create face indexes for Mesh grid
        rows, cols = X.shape
        faces = []
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Create two triangles per square
                idx1 = i * cols + j
                idx2 = i * cols + (j + 1)
                idx3 = (i + 1) * cols + j
                idx4 = (i + 1) * cols + (j + 1)
                faces.append([idx1, idx2, idx3])  # First triangle
                faces.append([idx2, idx4, idx3])  # Second triangle
        faces = np.array(faces, dtype=np.uint32)

        if hasattr(self, "mesh") and self.mesh is not None:
            self.mesh.parent = None  # Reset reference
        
        Z_flat = np.nan_to_num(Z_flat, nan=0.0, posinf=0.0, neginf=0.0)  # Replace NaN with None
        min_value = min(x for x in Z_flat if x is not None )

        Z_norm = (Z_flat - min_value) / (Z_flat.max() - min_value)  # Normalize
        Z_norm *= 100
        
        self.mesh = visuals.Mesh(vertices=np.column_stack((X_flat, Y_flat, Z_norm)),faces=faces , shading='smooth') 
        self.view.add(self.mesh)
        self.plot_3D_axes()
        self.view.camera.center = (result.shape[1]//2, -result.shape[0]//2, 0)
        self.canvas.draw()


    def plot_3D_axes(self):

        if hasattr(self, "ax_list") and self.ax_list is not None:
            for axis in self.ax_list:
                axis.parent = None  # Reset reference


        # Create X, Y, Z axes
        shape = self.data_img.shape
        x_axis = scene.Axis(pos=[[-1, 0], [shape[1], 0]], tick_direction=(100, -100), axis_color="red", tick_color="red")
        y_axis = scene.Axis(pos=[[0, 1], [0, -shape[0]]], tick_direction=(-100, 100), axis_color="green", tick_color="green")
        # z_axis = scene.Axis(pos=[[result.min(), 0], [result.max(), 0]], tick_direction=(0, -1), axis_color="blue", tick_color="blue")
        z_axis = scene.Axis(pos=[[0, 0], [100, 0]], tick_direction=(0, -1), axis_color="blue", tick_color="blue")

        z_axis.transform = scene.transforms.MatrixTransform()  # its acutally an inverted xaxis
        z_axis.transform.rotate(-90, (0, 1, 0))  # rotate cw around yaxis
        self.ax_list = (x_axis, y_axis, z_axis)
        for axis in self.ax_list:
            # axis.transform = scene.STTransform(scale=(1, 1, 1))  # Scale appropriately
            self.view.add(axis)  # Add to scene


    def on_mouse_click(self, event):
        """ Dynamically move the camera to focus on a clicked point. """
        if event.button == 3:  # Left-click only
            pos = event.pos  # Get mouse position
            picked = self.view.scene.node_transform(self.mesh).map(pos)  # Map to scene coords
            if picked is not None:
                self.view.camera.center = (picked[:3][0],-picked[:3][1],0 ) # Move camera to the clicked point
                print(f"Centered on: {picked[:3]}")  # Debugging


    def load(self, file_path, wavelenght, data_img):
        self.variable_init() # Clear all variables
        # Load the image and wavelengths
        self.file_path = file_path
        self.wavelengths = wavelenght
        self.data_img = data_img

        # Clear the axes
        if hasattr(self, "mesh") and self.mesh is not None:
            self.mesh.parent = None  # Reset reference
        custom_clear(self.axs[0])
        WL_MIN = wavelenght[0]
        # Display the image
        if WL_MIN <= 450:
            R = closest_id(700, wavelenght)
            G = closest_id(550, wavelenght)       
            B = closest_id(450, wavelenght)
            # print(f"RGB : {R}, {G}, {B}")
            # print(f"RGB : {wavelenght[R]}, {wavelenght[G]}, {wavelenght[B]}")
            RGB_img = self.data_img[:,:,(R,G,B)]


            if RGB_img.max()*2 < 1:
                try:
                    RGB_img = 2*RGB_img.view(np.ndarray)
                except ValueError:
                    pass
            self.axs[0].imshow(RGB_img)
        else:
            print("RGB values not supported")
        self.canvas.draw()



















class MyWindow(QMainWindow):
    # Define a signal that emits new width & height
    
    resized = Signal(int, int)
    def __init__(self):
        super().__init__()
        # Create an instance of CustomWidget and pass the resize signal
        self.widget = veget_indices()
        self.file_path ="D:/MAXIME/cours/4eme_annee/Projet_M1/wetransfer_data_m1_nantes_2025-03-25_1524/Data_M1_Nantes/VNIR(400-1000nm)/E2_Adm_On_J0_Pl1_F1_2.bil.hdr"
        img = sp.open_image(self.file_path)
        self.data_img = img.load()
        if 'wavelength' in img.metadata:
            self.wavelengths = img.metadata['wavelength']
        elif "Wavelength" in img.metadata:
            self.wavelengths = img.metadata['Wavelength']
        self.wavelengths = [float(i) for i in self.wavelengths]
        self.setCentralWidget(self.widget)

        self.resized.connect(lambda : self.widget.load(self.file_path, self.wavelengths, self.data_img))



    def resizeEvent(self, event):
        """ Emits the signal when the window is resized """
        new_width = self.width()
        new_height = self.height()
        self.resized.emit(new_width, new_height) 
        super().resizeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())