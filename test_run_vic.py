import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QTabWidget, QPushButton, QComboBox, QSizePolicy,  QFileDialog, QTextEdit, QSplitter, QProgressBar, QCheckBox, QRadioButton, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QFileDialog, QInputDialog
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui import QFont, QMovie
from superqt import QRangeSlider
from CustomElement import CustomWidgetRangeSlider
from Save_Import import Save_import
from Double_Curseur import Double_Curseur
from Trois_Slider import Trois_Slider
from Image_Mode_Slider import Image_Mode_Slider
from main_dessin_cluster import MainWindow_draw_cluster
from vegetation_indices_GPU import veget_indices_GPU
from main_double_kmean_sklearn import KMeansApp
import os
import spectral as sp
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from qtpy.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()
        self.save_import = Save_import()
        initial_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Image en couleur par défaut
        # self.matplotlib_widget_gris = MatplotlibImage_Gris(initial_image)
        self.matplotlib_widget_rgb = Image_Mode_Slider(initial_image)
        self.matplotlib_widget_double = Double_Curseur(initial_image)
        self.matplotlib_widget_3slid = Trois_Slider(initial_image)
        self.widget_drawcluster = MainWindow_draw_cluster()
        self.widget_veget_i = veget_indices_GPU()
        self.widget_KMeansApp = KMeansApp()

        self.save_import.matplotlib_widgets = [
            self.matplotlib_widget_rgb, 
            self.matplotlib_widget_double, 
            self.matplotlib_widget_3slid,
            ]
        
        


        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()

        self.tabs.addTab(self.tab1, "Accueil")
        self.tabs.addTab(self.tab2, "Unique WL")
        self.tabs.addTab(self.tab3, "Plage WL")
        self.tabs.addTab(self.tab4, "RGB-3sliders")
        self.tabs.addTab(self.tab5, "RGB-3sliders")
        self.tabs.addTab(self.tab6, "RGB-3sliders")
        self.tabs.addTab(self.tab7, "RGB-3sliders")

        self.tabs.setStyleSheet("""
            QTabBar::tab {
                color: white;
                font-family: 'Verdana';
                font-size: 14px;
                padding: 8px; 
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #4A4A4A;  /* Gris encore un peu plus clair pour l'onglet actif */
                font-weight: bold;
            }
        """)        

        self.save_import.import_button.clicked.connect(self.loading_file)


        layout = QHBoxLayout()
        layout.addWidget(self.save_import)
        self.tab1.setLayout(layout)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.matplotlib_widget_rgb)
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(self.matplotlib_widget_double)
        self.tab3.setLayout(layout3)

        layout4 = QVBoxLayout() 
        layout4.addWidget(self.matplotlib_widget_3slid)
        self.tab4.setLayout(layout4)

        layout5 = QVBoxLayout() 
        layout5.addWidget(self.widget_drawcluster)
        self.tab5.setLayout(layout5)

        layout6 = QVBoxLayout() 
        layout6.addWidget(self.widget_veget_i)
        self.tab6.setLayout(layout6)

        layout7 = QVBoxLayout() 
        layout7.addWidget(self.widget_KMeansApp)
        self.tab7.setLayout(layout7)


        self.setCentralWidget(self.tabs)
        # Global stylesheet
        self.setStyleSheet("""
        QWidget {}
        .MatplotlibImage {
            background-color: #2E2E2E;  /* Fond gris foncé */
        }
        .MatplotlibImage_3slid {
            background-color: #2E2E2E;  /* Fond gris foncé */
        }
        """)


    def loading_file(self):
        """ Load the file and update the widgets """
        self.matplotlib_widget_double.load_file(self.save_import.file_path_noload, self.save_import.wavelength, self.save_import.data_img)
        self.matplotlib_widget_rgb.load_file(self.save_import.file_path_noload, self.save_import.wavelength, self.save_import.data_img)
        self.matplotlib_widget_3slid.load_file(self.save_import.file_path_noload, self.save_import.wavelength, self.save_import.data_img)


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())