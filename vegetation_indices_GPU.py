import sys
import random
import spectral as sp
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog,QHBoxLayout,QMainWindow,QDialog,QLabel,QLineEdit,QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from CustomElement import CommentButton
import numpy as np


from utiles import closest_id, custom_clear,resolv_equation

from PySide6.QtCore import Signal

from vispy import scene
from vispy.scene import visuals


class veget_indices_GPU(QWidget):
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
        self.commentaire = None


    def init_ui(self):
        
        # Layouts
        layout = QVBoxLayout()
        figure_layout = QHBoxLayout()
        button_layout =  QHBoxLayout()
        toolbar_layout =  QHBoxLayout()

        # Matplotlib Figure and Canvas
        self.axs=[None]
        self.figure, self.axs[0] = plt.subplots(1, 1)
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        # self.figure.tight_layout()  # Applique à toute la figure
        self.canvas = FigureCanvas(self.figure)
        figure_layout.addWidget(self.canvas,1)

        # toolbar
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar_layout.addWidget(toolbar)

        # Comment button
        button_com = CommentButton(self)
        toolbar_layout.addWidget(button_com)
        layout.addLayout(toolbar_layout)

        # Create a VisPy canvas (GPU-rendered)
        self.SceneCanvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
        figure_layout.addWidget(self.SceneCanvas.native,1)
        layout.addLayout(figure_layout,1)

        # Create a 3D view
        self.view = self.SceneCanvas.central_widget.add_view()
        self.view.camera = 'turntable'  # Interactive 3D rotation
        self.view.camera.scale_factor = 600
        
        # Dropdown menu (ComboBox)
        self.dropdown = QComboBox()
        layout.addWidget(self.dropdown)

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.process_equation)
        button_layout.addWidget(self.plot_button)
     
        # Modify Equation button
        self.mod_eq_button = QPushButton("Modify Equation")
        self.mod_eq_button.clicked.connect(self.open_equation_editor)
        button_layout.addWidget(self.mod_eq_button)

        # New Equation button
        new_eq_button = QPushButton("New Equation")
        new_eq_button.clicked.connect(self.open_new_equation)
        button_layout.addWidget(new_eq_button)

        layout.addLayout(button_layout)

        self.populate_drop_down()
        
        self.setLayout(layout)
        # Connect mouse movement event
        self.SceneCanvas.events.mouse_press.connect(self.on_mouse_click)

       
    def populate_drop_down(self):
        """Reads the file, populates the dropdown, and adds tooltips."""
        file_path = "equations.txt"
        if file_path:
            self.dropdown.clear()  # Clear previous options
            self.equation_dict = {}
            with open(file_path, "r") as file:
                for line in file:
                    # Split each line into name and equation
                    parts = line.strip().split(":", 1)  # Split by the first colon
                    if len(parts) == 2:
                        name, equation = parts[0].strip(), parts[1].strip()
                        self.dropdown.addItem(name)  # Show only the name
                        self.dropdown.setItemData(self.dropdown.count() - 1, equation)  # Store equation as tooltip
                        self.equation_dict[name] = equation


    def open_new_equation(self):
            editor = NewEquation(self)
            if editor.exec_():  # If user clicked Save
                self.populate_drop_down()


    def open_equation_editor(self):
        current_name = self.dropdown.currentText()
        current_eq = self.dropdown.itemData(self.dropdown.currentIndex())
        editor = EquationEditor(self, name=current_name, equation=current_eq)
        
        if editor.exec_():
            action = editor.result
            if action[0] == "save":
                name, equation = action[1], action[2]
                self.equation_dict[name] = equation
            elif action[0] == "delete":
                name = action[1]
                if name in self.equation_dict:
                    del self.equation_dict[name]
            
            # Save all equations back to file
            with open("equations.txt", "w") as file:
                for name, equation in self.equation_dict.items():
                    file.write(f"{name}: {equation}\n")

            self.populate_drop_down()


    def process_equation(self):
        """
        Process the given equation to extract and compute values from hyperspectral data.
        """
        # equation = self.dropdown.currentText()
        self.axs[0].clear() 
        selected_index = self.dropdown.currentIndex()  # Get selected index
        equation = self.dropdown.itemData(selected_index)
        
        
        result = resolv_equation(equation,self.data_img,self.wavelengths)
        if result:
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
        z_axis = scene.Axis(pos=[[0, 0], [100, 0]], tick_direction=(0, -1), axis_color="blue", tick_color="blue")

        z_axis.transform = scene.transforms.MatrixTransform()  # its acutally an inverted xaxis
        z_axis.transform.rotate(-90, (0, 1, 0))  # rotate cw around yaxis
        self.ax_list = (x_axis, y_axis, z_axis)
        for axis in self.ax_list:
            self.view.add(axis)  # Add to scene


    def on_mouse_click(self, event):
        """ Dynamically move the camera to focus on a clicked point. """
        if hasattr(self, "mesh") and self.mesh is not None:
            if event.button == 3:  # Left-click only
                pos = event.pos  # Get mouse position
                x,y = self.view.scene.node_transform(self.mesh).map(pos)  # Map to scene coords
                if x is not None and y is not None:
                    [shapey, shapex, _]  = self.data_img.shape
                    width, height = self.SceneCanvas.size
                    x = int(x/width*shapex)     # Convert to image coordinates
                    y = int(y/height*shapey)    # Convert to image coordinates

                    self.view.camera.center = (x,-y,0 ) # Move camera to the clicked point


    def load_file(self, file_path, wavelenght, data_img):
        self.variable_init() # Clear all variables
        # Load the image and wavelengths
        self.file_path = file_path
        self.wavelengths = wavelenght
        self.data_img = data_img

        self.plot_3D_axes()

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
            RGB_img = self.data_img[:,:,(0,1,2)]
            self.axs[0].imshow(RGB_img)
            print("RGB values not supported")
        self.canvas.draw()













class EquationEditor(QDialog):
    def __init__(self, parent=None, name="", equation=""):
        super().__init__(parent)
        self.setWindowTitle("Equation Editor")
        self.name = name  # Store original name

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setText(name)

        self.eq_label = QLabel("Equation:")
        self.eq_input = QTextEdit()
        self.eq_input.setText(equation)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_equation)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_equation)
        self.delete_button.setStyleSheet("color: red;")

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.eq_label)
        layout.addWidget(self.eq_input)
        layout.addWidget(self.save_button)
        if name:  # Only show delete for existing equations
            layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.result = None  # Will store result status

    def save_equation(self):
        name = self.name_input.text().strip()
        equation = self.eq_input.toPlainText().strip()
        if name and equation:
            self.result = ("save", name, equation)
            self.accept()
        else:
            self.setWindowTitle("Please fill in both fields.")

    def delete_equation(self):
        self.result = ("delete", self.name)
        self.accept()





class NewEquation(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create or Edit Equation")

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.eq_label = QLabel("Equation:")
        self.eq_input = QTextEdit()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_equation)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.eq_label)
        layout.addWidget(self.eq_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_equation(self):
        name = self.name_input.text().strip()
        equation = self.eq_input.toPlainText().strip()

        if name and equation:
            with open("equations.txt", "a") as file:
                file.write(f"{name} : {equation}\n")
            self.accept()  # Close the dialog
        else:
            self.setWindowTitle("Please fill in both fields.")























class MyWindow(QMainWindow):
    # Define a signal that emits new width & height
    
    resized = Signal(int, int)
    def __init__(self):
        super().__init__()
        # Create an instance of CustomWidget and pass the resize signal
        self.widget = veget_indices_GPU()
        self.file_path ="D:/MAXIME/cours/4eme_annee/Projet_M1/wetransfer_data_m1_nantes_2025-03-25_1524/Data_M1_Nantes/VNIR(400-1000nm)/E2_Adm_On_J0_Pl1_F1_2.bil.hdr"
        img = sp.open_image(self.file_path)
        self.data_img = img.load()
        if 'wavelength' in img.metadata:
            self.wavelengths = img.metadata['wavelength']
        elif "Wavelength" in img.metadata:
            self.wavelengths = img.metadata['Wavelength']
        self.wavelengths = [float(i) for i in self.wavelengths]
        self.setCentralWidget(self.widget)

        self.resized.connect(lambda : self.widget.load_file(self.file_path, self.wavelengths, self.data_img))



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