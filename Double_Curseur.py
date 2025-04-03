import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QTabWidget, QPushButton, QComboBox, QSizePolicy,  QFileDialog, QTextEdit, QSplitter, QProgressBar, QCheckBox, QRadioButton, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QFileDialog, QInputDialog
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui import QFont, QMovie
from superqt import QRangeSlider
import main as m
from test3 import CustomWidgetRangeSlider

import os
import spectral as sp
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from qtpy.QtCore import Qt



class Double_Curseur(QWidget):
    def __init__(self, RGB_img, save_import):
        super().__init__()
        self.file_path = None
        self.file_data = None
        # self.setStyleSheet("background-color: #2E2E2E;")
        self.text = "Aucun commentaire effectué"

        # Création d'une figure avec 2 axes : 1 pour l'image et 1 pour le spectre
        self.figure, (self.Img_ax, self.spectrum_ax) = plt.subplots(1, 2, figsize=(15, 10), gridspec_kw={'width_ratios': [1, 1]})
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 0.5, 1])  # Image occupe 60% de la largeur
        self.spectrum_ax.set_position([0.6, 0.1, 0.5, 0.8])  # Augmenter la largeur
        self.figure.tight_layout()  # Applique à toute la figure
        self.canvas.setStyleSheet("background-color: #2E2E2E;")  # Application d'un fond gris

        # Toolbar pour la navigation
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        # Slider de contrôle pour les longueurs d'onde
        self.slider_widget = CustomWidgetRangeSlider()
        self.slider_widget.range_slider.sliderReleased.connect(self.update_image)
        self.slider_widget.range_slider.sliderReleased.connect(self.update_spectre)
        self.slider_widget.range_slider.valueChanged.connect(self.slider_widget.update_label)

        # Bouton pour importer le fichier
        self.import_button = QPushButton("Analyser")
        self.import_button.clicked.connect(self.import_file)
        self.fichier_selec = QLabel("Aucun fichier sélectionné")
        save_import.signals.fichier_importe.connect(self.update_file)

        self.comment = QPushButton("Commenter")
        self.comment.clicked.connect(self.commenter)


        # Layout pour les sliders et le bouton d'importation
        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
        import_layout.addWidget(self.comment)
        import_layout.setAlignment(self.comment, Qt.AlignRight)
        
        img_layout = QVBoxLayout()
        img_layout.addLayout(import_layout)
        img_layout.addWidget(toolbar)
        img_layout.addWidget(self.canvas)
        img_layout.addWidget(self.slider_widget)

        # Spectre
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='white')
        self.spectrum_ax.set_ylabel("Intensité", color='white')
        self.spectrum_ax.set_xlim(402, 998)
        self.spectrum_ax.tick_params(axis='x', colors='white')
        self.spectrum_ax.tick_params(axis='y', colors='white')

        # Données fictives pour le spectre (à remplacer par vos données réelles)
        self.spectrum_x = np.linspace(402, 998, 100)
        self.spectrum_y = np.zeros_like(self.spectrum_x)  # Spectre vide initial
        self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')

        

        self.setLayout(img_layout)

        # Affichage de l'image initiale
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_file(self, path):
        self.file_path = path
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI

    def update_image(self):
        idx_min, idx_max = self.slider_widget.range_slider.value()
        img_data = m.calcule_rgb_plage(self.file_data, self.metadata, idx_min, idx_max)
        img_array = np.array(img_data, dtype=np.uint8)
        self.Img_ax.clear()
        title = f"Image reconstituée entre {self.metadata['wavelength'][idx_min]} nm et {self.metadata['wavelength'][idx_max]} nm"
        self.Img_ax.imshow(img_array)
        self.Img_ax.set_title(title, fontsize=16, color='black', pad=20)  # Ajoute le titre

        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_spectre(self):
        wl_min, wl_max = self.slider_widget.range_slider.value()
        self.spectrum_ax.clear()

        self.spectrum_ax.plot(self.metadata["wavelength"][wl_min:wl_max], self.spectrum_y[wl_min:wl_max], color='cyan')

        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        self.spectrum_ax.set_ylabel("Intensité", color='black')
        self.spectrum_ax.set_xlim(self.metadata["wavelength"][wl_min], self.metadata["wavelength"][wl_max])
        self.spectrum_ax.set_xticks([self.metadata["wavelength"][wl_min], self.metadata["wavelength"][wl_max]])
        self.spectrum_ax.set_xticklabels([f"{float(self.metadata['wavelength'][wl_min]):.0f}", f"{float(self.metadata['wavelength'][wl_max]):.0f}"])
        # self.spectrum_ax.set_xticklabels(f"{self.metadata['wavelength'][wl_min]}", f"{self.metadata['wavelength'][wl_max]}")
        self.spectrum_ax.tick_params(axis='x', colors='black')
        self.spectrum_ax.tick_params(axis='y', colors='black')
        self.figure.tight_layout()
        self.canvas.draw()

    def import_file(self):
        self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        QApplication.processEvents()

        self.file_data = sp.open_image(self.file_path)
        self.img_data = self.file_data.load()  # Charger en tant que tableau NumPy
        self.metadata = self.file_data.metadata  # Récupérer les métadonnées
        self.imgopt = self.Img_ax.imshow(self.file_data[:,:,(0,1,2)])
        self.Img_ax.axis('off')

        img_data_calculated = m.calcule_rgb_plage(self.file_data, self.metadata, 0, int(self.metadata["bands"])-1)
        img_array = np.array(img_data_calculated, dtype=np.uint8)
        self.Img_ax.clear()
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()

        self.slider_widget.range_slider.setRange(0, int(self.metadata["bands"])-1)
        self.slider_widget.setWavelenghts(self.metadata["wavelength"])

        self.spectrum_ax.set_xlim(float(self.metadata["wavelength"][0]), float(self.metadata["wavelength"][-1]))
        self.spectrum_x = np.array(self.metadata["wavelength"])
        self.spectrum_x = self.spectrum_x.astype(float)
        self.spectrum_y = np.mean(self.img_data, axis=(0, 1))  # Moyenne des pixels par bande
        self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')

        self.fichier_selec.setText(os.path.basename(self.file_path))  # Afficher le chemin dans l'UI

    def commenter(self):
        self.text, ok = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "")

class SignalEmitter(QObject):
    fichier_importe = Signal(str)  # Signal émis lors de l'importation d'un fichier