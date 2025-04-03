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

from CustomElement import CustomCanvas,CustomToolbar,CustomWidgetRangeSlider, hyperspectral_appli
from utiles import mean_spectre_of_cluster, custom_clear

import re

import os
os.environ['OMP_NUM_THREADS'] = '4' 
np.random.seed(42)
sp.settings.envi_support_nonlowercase_params = True











class KMeansApp(hyperspectral_appli):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Means Clustering on HDR Images")
        self.variable_init()
        self.init_ui()


    def variable_init(self):
        self.param_has_changed_skm = True           # variables booleene pour signaler lorsqu'une modification a été faite aux parametre du clustering
        self.param_has_changed_spectra = True       #   
        self.file_path = None   # chemin d'acces du fichier HDR
        self.croped_wavelength = None   # liste des longueurs d'ondes comprises entre les valeurs min et max du double slider
        self.original_wavelengths = None    # liste de toutes les longueurs d'ondes enregistré par la cam
        self.data_img = None        
        self.first_cluster_map = None       # np.array de nombres entier positifs représentant les indices des clusters pour chaques pixels     
        self.second_cluster_map = None      # np.array de 0 et 1 représentant les indices de la feuille ou du background 
        self.WL_MIN = None        # la valeur de la plus petite longueur d'onde enregistré par la caméra (constante)
        self.wl_min_cursor = None       # l'inice de longueur d'onde min du slider
        self.wl_max_cursor = None       # l'inice de longueur d'onde max du slider

  


    def init_ui(self):

        layout = QVBoxLayout()

        # File Selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Aucun fichier sélectionné")
        file_button = QPushButton("Choisir un fichier")
        file_button.clicked.connect(self.load_file)
        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        # Matplotlib Figure
        self.figure, self.axs = plt.subplots(1, 2, figsize=(15, 10))
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.axs[0].set_title("hyperspectral image")
        self.axs[1].set_title("spectrum")
        self.canvas = CustomCanvas(self.figure, self.axs)
        layout.addWidget(CustomToolbar(self.canvas, self))
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
        self.btn_show_image.clicked.connect(self.display_image)
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
            self.croped_wavelength = self.original_wavelengths[self.wl_min_cursor:self.wl_max_cursor]
            # print("image data cropped between ",self.wavelengths[0]," and ", self.wavelengths[-1])



            
    
    def apply_first_kmean(self):
        if self.data_img is not None:
            if self.first_cluster_map is None: # on ne calcule les clusters que si les parametre ont changé ou si il n'existe pas deja de cluster map
                t1 = time()
                reshaped_data = self.data_img.reshape(-1, self.data_img.shape[-1]) # Reshape to (n_lines*n_colones, n_bands)
                kmeans = MiniBatchKMeans(n_clusters=2, n_init='auto', max_iter=10, random_state=42)
                labels = kmeans.fit_predict(reshaped_data[:,::10]) # uses a fraction of the bands for clustering to speed up the process
                self.first_cluster_map = labels.reshape(self.data_img.shape[:-1])
                print("first kmean executed in:", time()-t1)
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
                overlay = self.axs[0].imshow(mask, colorizer=color, alpha = 0.9,label=f"cluster{i}")
                overlay.set_cmap(plt.cm.colors.ListedColormap([color]))
            # self.axs[0].imshow(self.second_cluster_map, cmap='nipy_spectral')
            self.axs[0].axis('off')
            self.canvas.draw("legend")
    

    def display_spectra(self):

        if self.data_img is not None and self.second_cluster_map is not None and self.param_has_changed_spectra:
            custom_clear(self.axs[1])     # Clear the right graph
            self.axs[1].set_title("spectrum")
            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=self.second_cluster_map.min(), vmax=self.second_cluster_map.max())
            for i in np.unique(self.second_cluster_map):
                avg_spectrum = mean_spectre_of_cluster(self.second_cluster_map, self.data_img, selected_cluster_value=i)
                self.axs[1].plot(self.croped_wavelength, avg_spectrum, color=cmap(norm(i)), label=f"Cluster {i}")
            # Create the legend **AFTER** plotting all lines
            self.canvas.draw("legend")
            self.param_has_changed_spectra = False


    def on_click(self, event):
        """Handles mouse clicks on the left graph to get pixel coordinates."""
        if hasattr(event, "handled") and event.handled:  # If the event was marked as handled, ignore it
            return
        if event.inaxes == self.axs[0]:  # Check if click is on the left graph
            x, y = int(event.xdata), int(event.ydata)
            print("click event detected in left axs")

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

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMeansApp()
    window.show()
    sys.exit(app.exec())
