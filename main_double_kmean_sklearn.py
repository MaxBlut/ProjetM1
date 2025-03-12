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
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from CustomElement import CustomToolbar, PickableLegend 

import os
os.environ['OMP_NUM_THREADS'] = '4' 
np.random.seed(42)
sp.settings.envi_support_nonlowercase_params = True

class KMeansApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Means Clustering on HDR Images")
        self.wavelengths = None
        self.file_path = None
        self.data_img = None
        self.first_cluster_map = None
        self.second_cluster_map = None
        self.graph_dict = {} # Dictionary to store the graphs for toggling visibility and easy removal
        self.legend_obj = None
        self.legend_label = []
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
        self.canvas = FigureCanvas(self.figure)
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
        self.n_clusters_input = QLineEdit("6")
        self.n_iterations_input = QLineEdit("25")
        layout.addWidget(QLabel("Clusters:"))
        layout.addWidget(self.n_clusters_input)
        layout.addWidget(QLabel("Iterations:"))
        layout.addWidget(self.n_iterations_input)
        
        # Connect buttons
        self.btn_show_image.clicked.connect(self.display_image)
        self.btn_first_kmean.clicked.connect(self.apply_first_kmean)
        self.btn_second_kmean.clicked.connect(self.apply_second_kmean)
        self.btn_spectra.clicked.connect(self.display_spectra)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("pick_event", self.on_pick)
    
    def load_file(self):
        self.file_path = None
        self.data_img = None
        self.first_cluster_map = None
        self.second_cluster_map = None
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier HDR", "", "HDR Files (*.hdr)")
        if self.file_path:
            self.file_label.setText(f"Fichier : {self.file_path}")
            self.data_img = sp.open_image(self.file_path).load()
            self.wavelengths = [402 + 2 * i for i in range(self.data_img.shape[2])]
        self.axs[0].clear()
        self.axs[1].clear()
        self.display_image()
        self.canvas.draw()
    
    def display_image(self):
        if self.data_img is not None:
            self.axs[0].clear()
            wlMin = 402
            R = round((700-wlMin)/2) 
            G = round((550-wlMin)/2)
            B = round((450-wlMin)/2)
            RGB_img = self.data_img[:,:,(R,G,B)]
            if RGB_img.max()*2 < 1:
                try:
                    RGB_img = 2*RGB_img
                except ValueError:
                    pass
            self.axs[0].imshow(RGB_img)
            self.axs[0].axis('off')
            self.canvas.draw()
            
    
    def apply_first_kmean(self):
        if self.data_img is not None:
            t1 = time()
            reshaped_data = self.data_img.reshape(-1, self.data_img.shape[-1]) # Reshape to (n_lines*n_colones, n_bands)
            kmeans = MiniBatchKMeans(n_clusters=2, n_init='auto', max_iter=10, random_state=42)
            labels = kmeans.fit_predict(reshaped_data[:,::10]) # uses a fraction of the bands for clustering to speed up the process
            self.first_cluster_map = labels.reshape(self.data_img.shape[:-1])
            self.axs[0].clear()
            self.axs[0].imshow(self.first_cluster_map, cmap='nipy_spectral')
            self.axs[0].axis('off')
            self.canvas.draw()
            print("first kmean executed in:", time()-t1)
    

    def apply_second_kmean(self):
        if self.data_img is not None and self.first_cluster_map is not None:
            try:
                n_clusters = int(self.n_clusters_input.text())
                iterations = int(self.n_iterations_input.text())
            except ValueError:
                return
           
            mask = self.first_cluster_map == 1
            data_first_cluster = self.data_img[mask, :]
            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', max_iter=iterations, random_state=42)
            labels = kmeans.fit_predict(data_first_cluster)
            self.second_cluster_map = np.zeros_like(self.first_cluster_map, dtype=int)
            self.second_cluster_map[mask] = labels + 1
            
            self.axs[0].clear()
            self.axs[0].imshow(self.second_cluster_map, cmap='nipy_spectral')
            self.axs[0].axis('off')
            self.canvas.draw()
    

    def display_spectra(self):
        if self.data_img is not None and self.second_cluster_map is not None:
            self.axs[1].clear()     # Clear the right graph
            self.graph_dict = {}    # Reset the graph dictionary
            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=self.second_cluster_map.min(), vmax=self.second_cluster_map.max())
            # Store plotted lines
            plotted_lines = []
            
            for i in np.unique(self.second_cluster_map):
                mask = self.second_cluster_map == i
                avg_spectrum = np.mean(self.data_img[mask, :], axis=0)
                line, = self.axs[1].plot(self.wavelengths, avg_spectrum, color=cmap(norm(i)), label=f"Cluster {i}")
                plotted_lines.append(line)
                self.legend_label.append(f"Cluster {i}")
            # Create the legend **AFTER** plotting all lines
            legend = PickableLegend(self.axs[1], self.axs[1].get_lines(), self.legend_label)
            self.legend_obj = self.axs[1].add_artist(legend)

             # Store mapping of legend -> plot
            for legend_line, plot_line in zip(legend.get_lines(), plotted_lines):
                self.graph_dict[legend_line] = plot_line 

            self.canvas.draw()


    def on_click(self, event):
        """Handles mouse clicks on the left graph to get pixel coordinates."""
        if event.inaxes == self.axs[0]:  # Check if click is on the left graph
            x, y = int(event.xdata), int(event.ydata)

            # Identify the cluster under the click
            if self.first_cluster_map is not None:
                if self.first_cluster_map[y, x] != 1:
                    self.first_cluster_map = 1 - self.first_cluster_map
                    self.second_cluster_map = None

    def on_pick(self, event):
        """Handles pick events to toggle visibility of spectra."""
        print("picked")
        
        legend = event.artist
        isVisible = legend.get_visible()
        # Toggle visibility of the corresponding plot
        print("legende :" , legend)
        print("self.graph_dict : ", self.graph_dict)
        if legend in self.graph_dict:
            print("in the if")
            self.graph_dict[legend].set_visible(not isVisible)
            legend.set_visible(not isVisible)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMeansApp()
    window.show()
    sys.exit(app.exec())
