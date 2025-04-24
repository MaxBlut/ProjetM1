import sys
import spectral as sp
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
from time import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QLineEdit
)

from CustomElement import CustomCanvas,CustomToolbar,CustomWidgetRangeSlider,CommentButton
from utiles import mean_spectre_of_cluster, custom_clear, closest_id

from PySide6.QtCore import Signal, Qt

import re

import os
os.environ['OMP_NUM_THREADS'] = '4' 
np.random.seed(42)
sp.settings.envi_support_nonlowercase_params = True











class KMeansApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Means Clustering on HDR Images")
        self.variable_init()
        self.init_ui()


    def variable_init(self):
        self.commentaire = None
        self.param_has_changed_skm = True           # variables booleene pour signaler lorsqu'une modification a été faite aux parametre du clustering
        self.param_has_changed_spectra = True       #   
        self.file_path = None   # chemin d'acces du fichier HDR
        self.croped_wavelength = None   # liste des longueurs d'ondes comprises entre les valeurs min et max du double slider
        self.wavelengths = None    # liste de toutes les longueurs d'ondes enregistré par la cam
        self.data_img = None        
        self.first_cluster_map = None       # np.array de nombres entier positifs représentant les indices des clusters pour chaques pixels     
        self.second_cluster_map = None      # np.array de 0 et 1 représentant les indices de la feuille ou du background 
        self.WL_MIN = None        # la valeur de la plus petite longueur d'onde enregistré par la caméra (constante)
        self.wl_min_cursor = None       # l'inice de longueur d'onde min du slider
        self.wl_max_cursor = None       # l'inice de longueur d'onde max du slider
        if hasattr(self, "toolbar") and hasattr(self.toolbar, "number_of_overlay_ploted"):
            self.toolbar.number_of_overlay_ploted = 0

  


    def init_ui(self):

        layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()

        # Matplotlib Figure
        self.figure, self.axs = plt.subplots(1, 2, figsize=(15, 10))
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.axs[0].set_title("hyperspectral image")
        self.axs[1].set_title("spectrum")
        self.canvas = CustomCanvas(self.figure, self.axs)


        # toolbar
        self.toolbar = CustomToolbar(self.canvas, self)
        toolbar_layout.addWidget(self.toolbar)
        
        # button to add comment
        button_com = CommentButton(self)
        toolbar_layout.addWidget(button_com)

        layout.addLayout(toolbar_layout)

        layout.addWidget(self.canvas)
        # Buttons 
        btn_layout = QHBoxLayout()
        self.btn_show_image = QPushButton("Afficher Image")
        self.btn_first_kmean = QPushButton("Premier K-Means")
        self.btn_second_kmean = QPushButton("Deuxième K-Means")
        self.btn_spectra = QPushButton("Spectres Moyens")
        
        btn_layout.addWidget(self.btn_show_image)
        btn_layout.addWidget(self.btn_first_kmean)
        btn_layout.addWidget(self.btn_second_kmean)
        btn_layout.addWidget(self.btn_spectra)
        layout.addLayout(btn_layout)
        
        # KMeans parameters
        param_layout = QHBoxLayout()
        self.n_clusters_input = QLineEdit("6")
        self.n_iterations_input = QLineEdit("25")
        param_layout.addWidget(QLabel("Clusters:"))
        param_layout.addWidget(self.n_clusters_input)
        param_layout.addWidget(QLabel("Iterations:"))
        param_layout.addWidget(self.n_iterations_input)
        layout.addLayout(param_layout) 

        # Double slider
        self.slider_widget = CustomWidgetRangeSlider()
        self.slider_widget.range_slider.sliderReleased.connect(self.slider_value_changed) 
        self.slider_widget.range_slider.sliderReleased.connect(self.set_param_has_changed) 
        layout.addWidget(self.slider_widget)  

        # Connect text box signals
        self.n_clusters_input.textChanged.connect(self.set_param_has_changed)  
        self.n_iterations_input.textChanged.connect(self.set_param_has_changed)  
        
        # Connect buttons
        self.btn_show_image.clicked.connect(self.show_image)
        self.btn_first_kmean.clicked.connect(self.apply_first_kmean)
        self.btn_second_kmean.clicked.connect(self.apply_second_kmean)
        self.btn_spectra.clicked.connect(self.display_spectra)

        # self.canvas.mpl_connect("draw_event", self.update_legend) # emits signal when canvas is updated
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.setLayout(layout)


    def set_param_has_changed(self):
        """ Fonction permetant de positionné un flag a true pour forcer le second Kmean à se réexecuter au lieu de seulement s'afficher  """
        self.param_has_changed_skm = True 
    

    def slider_value_changed(self, value):
        """Restreint la valeur de data_img et wavelenght aux longeurs d'ondes compris entre le min et le max"""
        self.wl_min_cursor, self.wl_max_cursor= value  # Get slider positions
        if self.file_path :
            self.data_img = sp.open_image(self.file_path).load()[:,:,self.wl_min_cursor:self.wl_max_cursor]
            self.set_param_has_changed()
            self.croped_wavelength = self.wavelengths[self.wl_min_cursor:self.wl_max_cursor]
            



            
    
    def apply_first_kmean(self):
        if self.data_img is not None:
            if self.first_cluster_map is None: # on ne calcule les clusters que si les parametre ont changé ou si il n'existe pas deja de cluster map
                reshaped_data = self.data_img.reshape(-1, self.data_img.shape[-1]) # Reshape to (n_lines*n_colones, n_bands)
                kmeans = MiniBatchKMeans(n_clusters=2, n_init='auto', max_iter=10, random_state=42)
                labels = kmeans.fit_predict(reshaped_data[:,::10]) # uses a fraction of the bands for clustering to speed up the process
                self.first_cluster_map = labels.reshape(self.data_img.shape[:-1])
                self.param_has_changed_skm = True       # met la variable a True pour recharger le second Kmean
            custom_clear(self.axs[0])
            self.axs[0].set_title("hyperspectral image")
            self.axs[0].imshow(self.first_cluster_map, cmap='nipy_spectral')
            self.axs[0].axis('off')
            self.canvas.draw()
            

    def apply_second_kmean(self):
        if self.data_img is not None and self.first_cluster_map is not None: # si nous avons les données necessaire au second kmean
            try:
                n_clusters = int(self.n_clusters_input.text())
                iterations = int(self.n_iterations_input.text())
            except ValueError:
                print("value error in n_clusters or n_iterations")
                return
            if self.param_has_changed_skm or self.second_cluster_map is None: #on ne calcule les clusters que si les parametre ont changé ou si il n'existe pas deja de cluster map
                mask = self.first_cluster_map == 1
                data_first_cluster = self.data_img[mask, :]
                kmeans = KMeans(n_clusters=n_clusters, n_init='auto', max_iter=iterations, random_state=42)
                labels = kmeans.fit_predict(data_first_cluster)
                self.second_cluster_map = np.zeros_like(self.first_cluster_map, dtype=int)
                self.second_cluster_map[mask] = labels + 1
                self.param_has_changed_skm = False
                self.param_has_changed_spectra = True       # met la variable a True pour recharger le display spectra
            
            custom_clear(self.axs[0])   
            self.axs[0].set_title("hyperspectral image")
            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(0, len(np.unique(self.second_cluster_map)))
            
            for i in range(len(np.unique(self.second_cluster_map))):
                mask = self.second_cluster_map == i
                mask = np.ma.masked_where(~mask, mask)
                color = cmap(norm(i))
                overlay = self.axs[0].imshow(mask, alpha =1,label=f"cluster{i}")
                overlay.set_cmap(plt.cm.colors.ListedColormap([color]))
            # self.axs[0].imshow(self.second_cluster_map, cmap='nipy_spectral')
            self.axs[0].axis('off')
            self.canvas.draw("legend")
    

    def display_spectra(self):

        if self.data_img is not None and self.second_cluster_map is not None :
            custom_clear(self.axs[1])     # Clear the right graph
            self.axs[1].set_title("spectrum")
            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=self.second_cluster_map.min(), vmax=self.second_cluster_map.max())
            for i in np.unique(self.second_cluster_map):
                avg_spectrum = mean_spectre_of_cluster(self.second_cluster_map, self.data_img, selected_cluster_value=i)
                self.axs[1].plot(self.croped_wavelength, avg_spectrum, color=cmap(norm(i)), label=f"Cluster {i}")
            # Create the legend **AFTER** plotting all lines
            self.canvas.draw("legend")


    def on_click(self, event):
        """Handles mouse clicks on the left graph to get pixel coordinates."""
        if hasattr(event, "handled") and event.handled:  # If the event was marked as handled, ignore it
            return
        if event.inaxes == self.axs[0]:  # Check if click is on the left graph
            x, y = int(event.xdata), int(event.ydata)
            # Identify the cluster under the click
            if self.first_cluster_map is not None:
                if self.first_cluster_map[y, x] != 1:
                    self.first_cluster_map = 1 - self.first_cluster_map
                    self.second_cluster_map = None
                    self.param_has_changed_skm = True


    def merge_lines(self, lines):
        line_data = []
        for line in lines:
            line_data.append(line.get_ydata())
            line.remove()
        moyenne = np.mean(line_data,axis=0)
        self.axs[1].plot(self.croped_wavelength,moyenne, label="merged cluster")
        self.canvas.draw("legend")


    def load_file(self, file_path, wavelenghts, data_img):
        self.variable_init() # Clear all variables
        # Load the image and wavelengths
        self.file_path = file_path
        self.wavelengths = wavelenghts
        self.data_img = data_img
        self.croped_wavelength = self.wavelengths

        self.wl_min_cursor =self.wavelengths[0]
        self.wl_max_cursor =self.wavelengths[-1]
        self.slider_widget.setWavelenghts(self.wavelengths)
        custom_clear(self.axs[1])
        self.show_image()


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.toolbar.plot_overlay()
        else:
            super().keyPressEvent(event)

    
    def show_image(self):
        # Clear the axes
        custom_clear(self.axs[0])
        if self.data_img is not None:
            WL_MIN = self.wavelengths[0]
            # Display the image
            if WL_MIN <= 450:
                R = closest_id(700, self.wavelengths)
                G = closest_id(550, self.wavelengths)       
                B = closest_id(450, self.wavelengths)
                RGB_img = self.data_img[:,:,(R,G,B)]                
                if RGB_img.max()*2 < 1:
                    try:
                        RGB_img = 2*RGB_img.view(np.ndarray) # augmente la luminosité de l'image
                    except ValueError:
                        pass
                self.axs[0].imshow(RGB_img)
            else:
                RGB_img = self.data_img[:,:,(0,1,2)]
                self.axs[0].imshow(RGB_img)
                print("RGB values not supported")
            self.canvas.draw()















class MyWindow(QMainWindow):
    # Define a signal that emits new width & height
    
    resized = Signal(int, int)
    def __init__(self):
        super().__init__()
        # Create an instance of CustomWidget and pass the resize signal
        self.widget = KMeansApp()
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