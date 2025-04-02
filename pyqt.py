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



# Désactiver le mode interactif de matplotlib
plt.ioff()


class MatplotlibImage(QWidget):
    def __init__(self, RGB_img, save_import):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Écrivez ici une description ou un commentaire...")
        self.text_edit.setStyleSheet("background-color: #3A3A3A; color: white; font-size: 14px; padding: 5px; border-radius : 5px")
        self.file_path = None
        self.setStyleSheet("background-color: #2E2E2E;")
        
        # Création de la figure Matplotlib
        self.figure, self.Img_ax = plt.subplots(figsize=(10, 10), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.figure.patch.set_facecolor('#2E2E2E')

        # Barre d'outils Matplotlib
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        # Slider pour le réglage de la longueur d'onde
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(402, 998)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(2)
        self.slider.sliderReleased.connect(self.update_image)
        self.slider.valueChanged.connect(self.update_slider_text)

        self.slider.setStyleSheet("""
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

        # Labels
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Longueur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)

        self.left_label = QLabel("402 nm")
        self.left_label.setStyleSheet("color: white; font-size: 20px;")
        self.right_label = QLabel("998 nm")
        self.right_label.setStyleSheet("color: white; font-size: 20px;")
        self.choix_label = QLabel("Mode d'affichage :")
        self.choix_label.setStyleSheet("color: white; font-size: 20px;")
        self.choix_label.setFont(font)

        # Bouton "Importer fichier" (remplace l'ancien combo)
        self.import_button = QPushButton("Analyser")
        self.import_button.clicked.connect(self.import_file)

        self.comment = QPushButton("Commenter")
        self.comment.clicked.connect(self.commenter)

        
        self.fichier_selec = QLabel("Aucun fichier sélectionné")
        self.fichier_selec.setStyleSheet("color : #D3D3D3; font-size: 15px; font-style: italic;")
        save_import.signals.fichier_importe.connect(self.update_file)
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

        # Layout principal (image + sliders + import button)

        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
        import_layout.addWidget(self.comment)
        import_layout.setAlignment(self.comment, Qt.AlignRight)

        left_layout = QVBoxLayout()
        left_layout.addLayout(import_layout)
        left_layout.addWidget(toolbar)
        left_layout.addWidget(self.canvas)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.right_label)
        left_layout.addLayout(slider_layout)
        left_layout.addWidget(self.label)

        # Mode combo & bouton sauvegarde dans un layout vertical à droite
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #3A3A3A;
                color: white;
                font-family: 'Verdana';
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #4A4A4A;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background: #555;
            }
            QComboBox QAbstractItemView {
                background-color: #3A3A3A;
                color: white;
                selection-background-color: #4A4A4A;
            }
        """)
        self.mode_combo.addItems(["Couleur", "Gris", "RGB"])
        self.mode_combo.currentIndexChanged.connect(self.update_image)


        self.mode_combo.setMinimumWidth(200)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        right_layout = QVBoxLayout()
        right_layout.addStretch()  # Ajoute un espace flexible en haut
        right_layout.addWidget(self.choix_label)
        right_layout.addWidget(self.mode_combo)
                # Initialisation du QRangeSlider via la classe RangeSliderInitializer
    
        right_layout.addStretch()  # Ajoute un espace flexible en bas


        # Disposition globale : Image + contrôles à gauche | Mode combo & sauvegarde à droite
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_file(self, path):
        self.file_path = path
        print("je suis la")
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI


    def update_slider_text(self):
        wavelenght = self.slider.value()
        self.label.setText(f"Longueur d'onde : {wavelenght} nm")


    def update_image(self):
        wavelength = self.slider.value()
        # Switch-like behavior pour appliquer le bon cmap
        selected_mode = self.mode_combo.currentText()

        # Créer le titre dynamique
        title = f"Image reconstituée en mode {selected_mode} à la longueur d'onde {wavelength} nm"
        self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre au-dessus de l'image

        if selected_mode == "RGB":
            img_data = m.calcule_true_rgb_opti(wavelength, self.file_path)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en couleur
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Gris":
            img_data = m.calcule_true_gray_opti(wavelength, self.file_path)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array, cmap='gray')  # Affichage en niveaux de gris
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Couleur":
            img_data = m.calcule_true_gray_opti(wavelength, self.file_path)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en niveaux de gris            self.Img_ax.axis('off')
            self.canvas.draw()

    def import_file(self):

        self.file_path = sp.open_image(os.path.basename(self.file_path))
        self.img_data = self.file_path.load()  # Charger en tant que tableau NumPy
        self.metadata = self.file_path.metadata  # Récupérer les métadonnées
        self.left_label = QLabel(f"{self.metadata['wavelength'][0]} nm")
        self.right_label = QLabel(f"{self.metadata['wavelength'][-1]} nm")
        self.slider.setRange(float(self.metadata["wavelength"][0]), float(self.metadata["wavelength"][-1]))

    def commenter(self):
          self.text_matImage = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "")
class MatplotlibImage_DoubleCurseur(QWidget):
    def __init__(self, RGB_img, save_import):
        super().__init__()
        self.file_path = None
        self.file_data = None
        # self.setStyleSheet("background-color: #2E2E2E;")
        
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
        self.text_matDouble = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "")

class MatplotlibImage_DoubleCurseur2(QWidget):
    def __init__(self, RGB_img, save_import):
        super().__init__()
        self.file_data = None
        # self.setStyleSheet("background-color: #2E2E2E;")

        self.figure, self.Img_ax = plt.subplots(figsize=(5, 5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.figure.patch.set_facecolor('#2E2E2E')

        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        
        self.slider_widget = CustomWidgetRangeSlider()
        
        self.slider_widget.range_slider.sliderReleased.connect(self.update_image)
        self.slider_widget.range_slider.sliderReleased.connect(self.update_spectre)
        self.slider_widget.range_slider.valueChanged.connect(self.slider_widget.update_label)
        
        #LABELS---------------------------------------------
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Saisir une plage de longeur d'onde")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)
        
        self.left_label = QLabel("402 nm")
        self.left_label.setStyleSheet("color: white; font-size: 20px;")
        self.right_label = QLabel("998 nm")
        self.right_label.setStyleSheet("color: white; font-size: 20px;")

        #---------------- Bouton "Importer fichier" 
        self.import_button = QPushButton("Analyser")
        self.import_button.clicked.connect(self.import_file)
        self.fichier_selec = QLabel("Aucun fichier sélectionné")
        save_import.signals.fichier_importe.connect(self.update_file)

        self.fichier_selec.setStyleSheet("color : #D3D3D3; font-size: 15px; font-style: italic;")
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

        

        #LAYOUTS---------------------------------------------
    
        # ------------ LAYOUT IMPORT
        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
        import_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges autour du layout

        img_layout = QVBoxLayout()
        img_layout.addLayout(import_layout)
        img_layout.addWidget(toolbar)
        img_layout.addWidget(self.canvas)
        img_layout.addWidget(self.slider_widget)
        
        img_layout.addWidget(self.label)

         # SPECTRE ---------------------------------------------
        self.spectrum_figure, self.spectrum_ax = plt.subplots(figsize=(5, 5))
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        self.spectrum_ax.set_ylabel("Intensité", color='black')
        self.spectrum_ax.set_xlim(402, 998)
        self.spectrum_ax.tick_params(axis='x', colors='black')
        self.spectrum_ax.tick_params(axis='y', colors='black')

        # Génération de données fictives pour le spectre
        self.spectrum_x = np.linspace(402, 998, 100)  # Longueur d'onde fictive de 402 à 998 nm
        self.spectrum_y = np.zeros_like(self.spectrum_x)  # Spectre vide initial

        # Plot vide pour initialisation
        self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')

        main_layout = QHBoxLayout()
        main_layout.addLayout(img_layout, 1)
        main_layout.addWidget(self.spectrum_canvas, 1)

        self.setLayout(main_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()
        
    def update_file(self, path):
        self.file_path = path
        print("je suis la")
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI

    def update_image(self):
        idx_min, idx_max = self.slider_widget.range_slider.value()
        img_data = m.calcule_rgb_plage(self.file_data, self.metadata, idx_min, idx_max)
        img_array = np.array(img_data, dtype=np.uint8)
        self.Img_ax.clear()
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()
    
    def update_spectre(self):
        wl_min, wl_max = self.slider_widget.range_slider.value()
        print(wl_min, wl_max)
        print(self.spectrum_y[wl_min:wl_max])
        
        self.spectrum_ax.clear()

        self.spectrum_ax.plot(self.metadata["wavelength"][wl_min:wl_max], self.spectrum_y[wl_min:wl_max], color='cyan')


        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        self.spectrum_ax.set_ylabel("Intensité", color='black')
        self.spectrum_ax.set_xlim(self.metadata["wavelength"][wl_min], self.metadata["wavelength"][wl_max])
        self.spectrum_ax.set_xticks([self.metadata["wavelength"][wl_min], self.metadata["wavelength"][wl_max]])
        self.spectrum_ax.set_xticklabels([f"{float(self.metadata['wavelength'][wl_min]):.0f}",
                                  f"{float(self.metadata['wavelength'][wl_max]):.0f}"])
        self.spectrum_ax.tick_params(axis='x', colors='black')
        self.spectrum_ax.tick_params(axis='y', colors='black')
        self.spectrum_figure.tight_layout()
        self.spectrum_canvas.draw()

    def import_file(self):

        self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        # Afficher l'animation de chargement
        QApplication.processEvents() 
        
        
        # Stopper l'animation après le chargement
        
        self.file_data = sp.open_image(self.file_path)
        self.img_data = self.file_data.load()  # Charger en tant que tableau NumPy
        self.metadata = self.file_data.metadata  # Récupérer les métadonnées
        self.imgopt = self.Img_ax.imshow(self.file_data[:,:,(0,1,2)])
        self.Img_ax.axis('off')

        img_data_calculated = m.calcule_rgb_plage(self.file_data, self.metadata,0, int(self.metadata["bands"])-1)
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
        self.spectrum_y = np.mean(self.img_data, axis=(0,1))  # Moyenne des pixels par bande
        self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')

        self.fichier_selec.setText(os.path.basename(self.file_path))  # Afficher le chemin dans l'UI

class MatplotlibImage_3slid(QWidget):
    def __init__(self, RGB_img, save_import):
        super().__init__()
        self.file_path = None

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
        save_import.signals.fichier_importe.connect(self.update_file)

        self.comment = QPushButton("Commenter")
        self.comment.cliked.connect(self.commenter())


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
        # self.spectrum_figure, self.spectrum_ax = plt.subplots(figsize=(5, 5))
        # self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='white')
        self.spectrum_ax.set_ylabel("Intensité", color='white')
        self.spectrum_ax.set_xlim(0, 0)
        self.spectrum_ax.tick_params(axis='x', colors='white')
        self.spectrum_ax.tick_params(axis='y', colors='white')
        # Graphique vide au départ (sans données)
        self.spectrum_ax.bar([], [], color=['red', 'green', 'blue'])  # Barres vides
        self.spectrum_ax.set_title("Réflectance en fonction de la longueur d'onde")
        self.canvas.draw()




        self.setLayout(img_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_file(self, path):
        self.file_path = path
        print("je suis la")
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI

    def update_slid_text(self):
        # Récupérer les valeurs des sliders
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()

        # Mettre à jour le texte des labels
        self.value_r.setText(f"{self.metadata['wavelength'][wl_r]} nm")
        self.value_g.setText(f"{self.metadata['wavelength'][wl_g]} nm")
        self.value_b.setText(f"{self.metadata['wavelength'][wl_b]} nm")

        # Afficher la valeur des sliders sous forme de tooltip
        self.slid_r.setToolTip(f"{self.metadata['wavelength'][wl_r]} nm")
        self.slid_g.setToolTip(f"{self.metadata['wavelength'][wl_g]} nm")
        self.slid_b.setToolTip(f"{self.metadata['wavelength'][wl_b]} nm")


    def update_image(self):


        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()
        title = f"Image reconstituée interpretant la longueur d'onde R comme {self.metadata['wavelength'][wl_r]} nm, G: {self.metadata['wavelength'][wl_g]} nm, B: {self.metadata['wavelength'][wl_b]} nm"
        self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre

        self.imgopt.set_data(self.file_data[:, :, (wl_r, wl_g, wl_b)])
        self.canvas.draw_idle()



    def import_file(self):
        self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        # Afficher l'animation de chargement
        QApplication.processEvents() 
        
        # Stopper l'animation après le chargement
        
        self.file_data = sp.open_image(self.file_path)
        self.img_data = self.file_data.load()  # Charger en tant que tableau NumPy
        self.metadata = self.file_data.metadata  # Récupérer les métadonnées
        self.imgopt = self.Img_ax.imshow(self.file_data[:,:,(0,1,2)])
        self.Img_ax.axis('off')

        # Charger le fichier HDR

        self.slid_r.setRange(0, int(self.metadata["bands"])-1)
        self.slid_g.setRange(0, int(self.metadata["bands"])-1)
        self.slid_b.setRange(0, int(self.metadata["bands"])-1)

        self.spectrum_ax.set_xlim(float(self.metadata["wavelength"][0]), float(self.metadata["wavelength"][-1]))
        
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
        if self.img_data is None or self.metadata is None:
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
        wavelengths = [self.metadata['wavelength'][self.slid_r.value()],self.metadata['wavelength'][self.slid_g.value()], self.metadata['wavelength'][self.slid_b.value()]]
        reflectance_values = []

        # Conversion des longueurs d'onde en indices de bande
        wavelengths_available = np.array(self.metadata['wavelength'], dtype=float)
        for wl in wavelengths:
            idx = np.abs(wavelengths_available - float(wl)).argmin()
            reflectance_values.append(self.img_data[y, x, idx])

        # Mise à jour de l'affichage
        self.update_spectrum(wavelengths, reflectance_values)

    def commenter(self):
        self.text_mat3slid = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "")
class Save_import(QWidget):

    def __init__(self, matplotlib_widgets=None):
        super().__init__()
        self.signals = SignalEmitter()  # Signal émis lors de l'importation d'un fichier
        self.matplotlib_widgets = matplotlib_widgets  # Liste de widgets Matplotlib à enregistrer

        self.file_path_noload = None
        self.matplotlib_widgets = matplotlib_widgets if matplotlib_widgets is not None else []  

        #---------------- Bouton "Importer fichier" 
        self.import_button = QPushButton("Importer fichier")
        self.import_button.clicked.connect(self.import_file)
        self.fichier_selec = QLabel("Aucun fichier sélectionné")
        self.fichier_selec.setStyleSheet("color : #D3D3D3; font-size: 15px; font-style: italic;")
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

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Écrivez ici une description ou un commentaire...")
        self.text_edit.setStyleSheet("background-color: #3A3A3A; color: white; font-size: 14px; padding: 5px; border-radius : 5px")
        self.file_path = None
        self.setStyleSheet("background-color: #2E2E2E;")

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_all_as_pdf)

        self.save_button.setMinimumWidth(200)
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)

        import_layout = QHBoxLayout()
        import_layout.addStretch()  # Ajoute un espace flexible en haut
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
        import_layout.addStretch()  # Ajoute un espace flexible en bas

        save_layout = QVBoxLayout()
        save_layout.addWidget(self.text_edit)
        save_layout.addWidget(self.save_button)

        # Disposition globale : Image + contrôles à gauche | Mode combo & sauvegarde à droite

        main_layout = QHBoxLayout()
        main_layout.addLayout(import_layout, 3)
        main_layout.addLayout(save_layout, 1)
        self.setLayout(main_layout)


    def save_all_as_pdf(self):

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer sous", "", "Fichier PDF (*.pdf)")
        if not file_path:
            return

        # Création d'un seul PDF
        pdf_canvas = canvas.Canvas(file_path, pagesize=A4)
        page_width, page_height = A4

        commentaires = []
        commentaires.append(self.)
        for i, widget in enumerate(self.matplotlib_widgets):
            text, ok = QInputDialog.getMultiLineText(self, "Ajouter un commentaire",
                                                     f"Commentaire pour l'image {i+1} :", "")
            if not ok:  
                text = "Pas de commentaire."
            commentaires.append(text)

        for i, widget in enumerate(self.matplotlib_widgets):
            if hasattr(widget, 'figure'):  # Vérifier si le widget a bien une figure Matplotlib
                temp_img_path = f"temp_image_{i}.png"  # Nom unique pour chaque figure
                widget.figure.canvas.draw()  # Forcer le dessin de la figure avant de la sauvegarder

                widget.figure.savefig(temp_img_path, dpi=300, bbox_inches='tight')

                img = Image.open(temp_img_path)
                img.show()
                img_width, img_height = img.size
                scale = min(page_width / img_width, (page_height - 100) / img_height)
                new_width = img_width * scale
                new_height = img_height * scale

                x_offset = (page_width - new_width) / 2
                y_offset = page_height - new_height - 50
                pdf_canvas.drawImage(temp_img_path, x_offset, y_offset, width=new_width, height=new_height)
                 # Ajouter le commentaire sous l'image
                pdf_canvas.setFont("Helvetica", 12)
                y_pos = y_offset - 20
                for line in commentaires[i].split("\n"):
                    pdf_canvas.drawString(50, y_pos, line)
                    y_pos -= 15

                pdf_canvas.showPage()  # Nouvelle page pour chaque image

        pdf_canvas.save()
        print(f"PDF enregistré à : {file_path}")

    def import_file(self):
        options = QFileDialog.Options()
        self.file_path_noload, _ = QFileDialog.getOpenFileName(
            self, "Importer un fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt)", options=options)

        if not self.file_path_noload:  # Vérifie si un fichier a été sélectionné
            print("Aucun fichier sélectionné.")
            return
        self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        QApplication.processEvents() 

        self.fichier_selec.setText(os.path.basename(self.file_path_noload))  # Afficher le chemin dans l'UI
        self.signals.fichier_importe.emit(self.file_path_noload)  # Émet le signal avec le chemin du fichier
        print("Signal émis")
    
    def get_fichier(self):
        if self.file_path_noload is None:
            return None
        else:
            return self.file_path_noload

class SignalEmitter(QObject):
    fichier_importe = Signal(str)  # Signal émis lors de l'importation d'un fichier

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()
        self.save_import = Save_import()

        
        initial_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Image en couleur par défaut
        # self.matplotlib_widget_gris = MatplotlibImage_Gris(initial_image)
        self.matplotlib_widget_rgb = MatplotlibImage(initial_image, self.save_import)
        self.matplotlib_widget_double = MatplotlibImage_DoubleCurseur(initial_image,self.save_import)
        self.matplotlib_widget_3slid = MatplotlibImage_3slid(initial_image,self.save_import)

        self.save_import.matplotlib_widgets = [
            self.matplotlib_widget_rgb, 
            self.matplotlib_widget_double, 
            self.matplotlib_widget_3slid]
        self.save_import.signals.fichier_importe.connect(self.matplotlib_widget_rgb.update_file)
        self.save_import.signals.fichier_importe.connect(self.matplotlib_widget_double.update_file)
        self.save_import.signals.fichier_importe.connect(self.matplotlib_widget_3slid.update_file)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.addTab(self.tab1, "Accueil")
        self.tabs.addTab(self.tab2, "Unique WL")
        self.tabs.addTab(self.tab3, "Plage WL")
        self.tabs.addTab(self.tab4, "RGB-3sliders")

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



if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
