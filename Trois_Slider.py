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

import os
import spectral as sp
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from qtpy.QtCore import Qt



class Trois_Slider(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.file_path = None
        self.img_data = None
        self.wavelength = None
        self.text = "Aucun commentaire effectué"
        self.setStyleSheet("background-color: #2E2E2E;")
        
        self.figure, (self.Img_ax, self.spectrum_ax) = plt.subplots(1, 2,figsize=(15, 10), gridspec_kw={'width_ratios': [3, 2]})
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.figure.patch.set_facecolor('#2E2E2E')

        self.Img_ax.set_position([0, 0, 0.6, 1])  # Image sur 60% de la largeur
        self.spectrum_ax.set_position([0.65, 0.1, 0.35, 0.8])  # Spectre sur 40% avec un petit décalage
        self.canvas.mpl_connect('button_press_event', self.on_click)



        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        #SLIDER 
        self.slid_r = QSlider(Qt.Horizontal)
        self.slid_r.setRange(0, 0)
        self.slid_r.setTickPosition(QSlider.TicksBelow)
        self.slid_r.setTickInterval(2)
        self.slid_r.setSingleStep(2)
        self.slid_r.valueChanged.connect(self.update_slid_text)
        self.slid_r.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        #self.slid_r.sliderReleased.connect(self.update_spectrum)

        self.slid_g = QSlider(Qt.Horizontal)
        self.slid_g.setRange(0,0)
        self.slid_g.setTickPosition(QSlider.TicksBelow)
        self.slid_g.setTickInterval(2)
        self.slid_g.setSingleStep(2)
        self.slid_g.valueChanged.connect(self.update_slid_text)
        self.slid_g.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        #self.slid_g.sliderReleased.connect(self.update_spectrum)

        self.slid_b = QSlider(Qt.Horizontal)
        self.slid_b.setRange(0, 0)
        self.slid_b.setTickPosition(QSlider.TicksBelow)
        self.slid_b.setTickInterval(2)
        self.slid_b.setSingleStep(2)
        self.slid_b.valueChanged.connect(self.update_slid_text)
        self.slid_b.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        #self.slid_b.sliderReleased.connect(self.update_spectrum)

        StyleSheet=("""
    QSlider::groove:horizontal {
        border: 1px solid #bbb;
        background: #ddd;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::handle:horizontal {
        background: #0078D7; /* Bleu Windows */
        border: 1px solid #005A9E;
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }

    QSlider::handle:horizontal:hover {
        background: #005A9E; /* Bleu foncé au survol */
    }
""")
        self.slid_r.setStyleSheet(StyleSheet)
        self.slid_g.setStyleSheet(StyleSheet)
        self.slid_b.setStyleSheet(StyleSheet)

        #---------------- Bouton "Importer fichier" 
        self.import_button = QPushButton("Analyser")
        self.import_button.clicked.connect(self.import_file)
        self.fichier_selec = QLabel("Aucun fichier sélectionné")
        self.fichier_selec.setStyleSheet("color : #D3D3D3; font-size: 15px; font-style: italic;")

        self.comment = QPushButton("Commenter")
        self.comment.clicked.connect(self.commenter)

        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)

        # Création des labels
        self.r_label = QLabel("R")
        self.g_label = QLabel("G")
        self.b_label = QLabel("B")

        # Appliquer un style aux labels pour qu'ils soient colorés et lisibles
        self.r_label.setStyleSheet("color: red; font-size: 20px; font-weight: bold;")
        self.g_label.setStyleSheet("color: green; font-size: 20px; font-weight: bold;")
        self.b_label.setStyleSheet("color: blue; font-size: 20px; font-weight: bold;")

        # LABELS AU DSSUS --------------------------------
        self.value_r = QLabel(" veuillez analyser le fichier")
        self.value_r.setAlignment(Qt.AlignCenter)
        self.value_r.setStyleSheet("color: white; font-size: 16px;")

        self.value_g = QLabel("")
        self.value_g.setAlignment(Qt.AlignCenter)
        self.value_g.setStyleSheet("color: white; font-size: 16px;")

        self.value_b = QLabel("")
        self.value_b.setAlignment(Qt.AlignCenter)
        self.value_b.setStyleSheet("color: white; font-size: 16px;")

        # ------ LAYOUT ------
        self.r_slidtex = QVBoxLayout()
        self.r_slidtex.addWidget(self.value_r)
        self.r_slidtex.addWidget(self.slid_r)

        self.g_slidtex = QVBoxLayout()
        self.g_slidtex.addWidget(self.value_g)
        self.g_slidtex.addWidget(self.slid_g)

        self.b_slidtex = QVBoxLayout()
        self.b_slidtex.addWidget(self.value_b)
        self.b_slidtex.addWidget(self.slid_b)

        # LAYOUT SLID --------------------------------------
        self.r_layout = QHBoxLayout()
        self.r_layout.addWidget(self.r_label)
        self.r_layout.addLayout(self.r_slidtex)

        self.g_layout = QHBoxLayout()
        self.g_layout.addWidget(self.g_label)
        self.g_layout.addLayout(self.g_slidtex)

        self.b_layout = QHBoxLayout()
        self.b_layout.addWidget(self.b_label)
        self.b_layout.addLayout(self.b_slidtex)

        # Ajout des layouts dans le layout principal
        slider_layout = QVBoxLayout()
        slider_layout.addLayout(self.r_layout)
        slider_layout.addLayout(self.g_layout)
        slider_layout.addLayout(self.b_layout)

        #LABELS---------------------------------------------
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Choisir des longueurs d'onde pour les canaux R, G, B")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)

       
        #LAYOUTS---------------------------------
        # ------------
        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
        import_layout.addWidget(self.comment)
        import_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges autour du layout

        import_layout.setAlignment(self.comment, Qt.AlignRight)

        img_layout = QVBoxLayout()
        img_layout.addLayout(import_layout)
        img_layout.addWidget(toolbar)
        img_layout.addWidget(self.canvas)
        img_layout.addLayout(slider_layout)
        img_layout.addWidget(self.label)
        img_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges autour du layout

        #Création de l'affichage du spectre

        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='white')
        self.spectrum_ax.set_ylabel("Intensité", color='white')
        self.spectrum_ax.set_xlim(0, 0)
        self.spectrum_ax.tick_params(axis='x', colors='white')
        self.spectrum_ax.tick_params(axis='y', colors='white')
        # Graphique vide au départ (sans données)
        self.spectrum_ax.bar([], [], color=['red', 'green', 'blue'])  # Barres vides
        self.spectrum_ax.set_title("Réflectance en fonction de la longueur d'onde")
        self.canvas.draw()

        self.figure.tight_layout()
        self.figure.tight_layout()

        self.setLayout(img_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_file(self, path):
        self.file_path = path
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI

    def update_slid_text(self):
        # Récupérer les valeurs des sliders
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()

        # Mettre à jour le texte des labels
        self.value_r.setText(f"{self.wavelength[wl_r]} nm")
        self.value_g.setText(f"{self.wavelength[wl_g]} nm")
        self.value_b.setText(f"{self.wavelength[wl_b]} nm")

        # Afficher la valeur des sliders sous forme de tooltip
        self.slid_r.setToolTip(f"{self.wavelength[wl_r]} nm")
        self.slid_g.setToolTip(f"{self.wavelength[wl_g]} nm")
        self.slid_b.setToolTip(f"{self.wavelength[wl_b]} nm")


    def update_image(self):


        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()
        title = f"Image reconstituée interpretant la longueur d'onde R comme {self.wavelength[wl_r]} nm, G: {self.wavelength[wl_g]} nm, B: {self.wavelength[wl_b]} nm"
        self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre

        self.imgopt.set_data(self.img_data[:, :, (wl_r, wl_g, wl_b)])
        self.canvas.draw_idle()



    def load_file(self, file_path, wavelength, data_img):
        self.wavelength = wavelength
        self.file_path = file_path
        self.img_data = data_img
        # self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        # # Afficher l'animation de chargement
        # QApplication.processEvents() 
        
        # Stopper l'animation après le chargement
        
        # self.file_data = sp.open_image(self.file_path)
        # self.img_data = self.file_data.load()  # Charger en tant que tableau NumPy
        # self.metadata = self.file_data.metadata  # Récupérer les métadonnées
        self.imgopt = self.Img_ax.imshow(self.img_data[:,:,(0,1,2)])
        self.Img_ax.axis('off')

        # Charger le fichier HDR

        self.slid_r.setRange(0, len(self.wavelength)-1)
        self.slid_g.setRange(0, len(self.wavelength)-1)
        self.slid_b.setRange(0, len(self.wavelength)-1)

        self.spectrum_ax.set_xlim(float(self.wavelength[0]), float(self.wavelength[-1]))
        
        self.value_r.setText(" Choisissez une longueur d'onde")
        self.value_g.setText(" ")
        self.value_b.setText(" ")

        self.fichier_selec.setText(os.path.basename(self.file_path))  # Afficher le chemin dans l'UI
    
    def update_spectrum(self,  wavelengths, reflectance_values):
        self.spectrum_ax.clear()
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)")
        self.spectrum_ax.set_ylabel("Réflectance")
        self.spectrum_ax.set_ylim(0, 1)

        # Positions équidistantes pour les barres
        x_positions = np.arange(len(wavelengths))  # [0, 1, 2] pour 3 couleurs

        # Création du diagramme en barres avec largeur fine
        colors = ['red', 'green', 'blue']
        self.spectrum_ax.bar(x_positions, reflectance_values, color=colors, width=0.2)

        # Remettre les vraies longueurs d'onde en labels sur l'axe X
        self.spectrum_ax.set_xticks(x_positions)
        self.spectrum_ax.set_xticklabels(wavelengths)
        self.figure.tight_layout()
        self.canvas.draw()  # Rafraîchir l'affichage

    def on_click(self, event):
        if self.img_data is None:
            print("Aucune image hyperspectrale chargée.")
            return

        if event.inaxes != self.Img_ax:
            return

        x, y = int(event.xdata), int(event.ydata)
        print(f"Pixel cliqué : ({x}, {y})")

        # Vérification que les longueurs d'onde existent
        if "wavelength" not in self.metadata:
            print("Métadonnées de longueurs d'onde introuvables.")
            return

        # Récupération des longueurs d'onde choisies
        wavelengths = [self.wavelength[self.slid_r.value()],self.wavelength[self.slid_g.value()], self.wavelength[self.slid_b.value()]]
        reflectance_values = []

        # Conversion des longueurs d'onde en indices de bande
        wavelengths_available = np.array(self.wavelength, dtype=float)
        for wl in wavelengths:
            idx = np.abs(wavelengths_available - float(wl)).argmin()
            reflectance_values.append(self.img_data[y, x, idx])

        # Mise à jour de l'affichage
        self.update_spectrum(wavelengths, reflectance_values)

    def commenter(self):
        self.text, ok = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "") 

