import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QComboBox, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QFont
from utiles import calcule_true_rgb_opti, calcule_true_gray_opti

import os
import spectral as sp
import time
from reportlab.lib.pagesizes import A4

from qtpy.QtCore import Qt

from CustomElement import CommentButton

from time import time

# Désactiver le mode interactif de matplotlib
plt.ioff()


class Image_Mode_Slider(QWidget):
    def __init__(self):
        super().__init__()
        self.variable_init()
        self.init_ui()

    
    def variable_init(self):
        self.wavelength = None
        self.img_data = None    
        self.file_path = None
        self.file_path = None
        self.commentaire = None


    def init_ui(self):

        # Layout
        main_layout = QVBoxLayout()
        canvas_layout = QHBoxLayout()
        import_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()
        slider_layout = QHBoxLayout()

        # Création de la figure Matplotlib
        self.figure, self.Img_ax = plt.subplots(figsize=(10, 10), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.Img_ax.axis('off')



        # Barre d'outils Matplotlib
        toolbar = NavigationToolbar(self.canvas, self)
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)
        toolbar_layout.addWidget(toolbar)

        # button to add comment
        button_com = CommentButton(self)
        toolbar_layout.addWidget(button_com)

        # Slider pour le réglage de la longueur d'onde
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(2)
        self.slider.sliderReleased.connect(self.update_image)
        self.slider.valueChanged.connect(self.update_slider_text)
        self.slider.actionTriggered.connect(self.handle_slider_action)

        # Labels
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Longueur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)

        self.left_label = QLabel("0 nm")
        self.right_label = QLabel("0 nm")
        self.choix_label = QLabel("Mode d'affichage :")
        self.choix_label.setFont(font)


        left_layout.addLayout(import_layout)
        left_layout.addWidget(self.canvas,1)

        
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.right_label)
        left_layout.addLayout(slider_layout)
        left_layout.addWidget(self.label)

        # Mode combo & bouton sauvegarde dans un layout vertical à droite
        self.mode_combo = QComboBox()
        
        self.mode_combo.addItems(["Couleur", "Gris", "RGB"])
        self.mode_combo.currentIndexChanged.connect(self.update_image)


        self.mode_combo.setMinimumWidth(200)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)



        right_layout.addStretch()  # Ajoute un espace flexible en haut
        right_layout.addWidget(self.choix_label)
        right_layout.addWidget(self.mode_combo)
    
        right_layout.addStretch()  # Ajoute un espace flexible en bas


        # Disposition globale : Image + contrôles à gauche | Mode combo & sauvegarde à droite
        
        canvas_layout.addLayout(left_layout, 3)
        canvas_layout.addLayout(right_layout, 1)

        main_layout.addLayout(toolbar_layout, 1)
        main_layout.addLayout(canvas_layout, 9)

        self.setLayout(main_layout)

    def update_file(self, path):
        self.file_path = path
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI


    def update_slider_text(self):
        wavelenght = self.slider.value()
        self.label.setText(f"Longueur d'onde : {self.wavelength[wavelenght]} nm")


    def update_image(self):
        if self.wavelength is not None:
            idx_wavelength = self.slider.value()
            # Switch-like behavior pour appliquer le bon cmap
            selected_mode = self.mode_combo.currentText()

            # Créer le titre dynamique
            title = f"Image reconstituée en mode {selected_mode} à la longueur d'onde {self.wavelength[idx_wavelength]} nm"
            self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre au-dessus de l'image
            self.Img_ax.clear()
            if selected_mode == "RGB":
                img_data = calcule_true_rgb_opti(idx_wavelength, self.open_file, self.wavelength)
                img_array = np.array(img_data, dtype=np.uint8)
                self.Img_ax.imshow(img_array)  # Affichage en couleur
                

            elif selected_mode == "Gris":
                self.Img_ax.imshow(self.img_data[:,:,idx_wavelength], cmap='gray')  # Affichage en niveaux de gris

            elif selected_mode == "Couleur":
                self.Img_ax.imshow(self.img_data[:,:,idx_wavelength])  # Affichage en niveaux de gris

            self.canvas.draw()


    def handle_slider_action(self, action):
        if action ==3 or action == 4:  # 3 => jump-by-10-ticks right , 4 = jump-by-10-ticks left 
            self.update_image()




    def load_file(self, file_path, wavelength, data_img):
        self.wavelength = wavelength
        self.file_path = file_path
        self.img_data = data_img
        self.open_file = sp.open_image(self.file_path)
        self.left_label.setText(f"{self.wavelength[0]} nm")
        self.right_label.setText(f"{self.wavelength[-1]} nm")
        self.slider.setRange(0, len(self.wavelength)-1)
        self.update_image()


