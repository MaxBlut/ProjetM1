import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QTabWidget, QPushButton, QComboBox, QSizePolicy,  QFileDialog, QTextEdit, QSplitter, QProgressBar, QCheckBox, QRadioButton, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QFileDialog, QInputDialog
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui import QFont, QMovie
from superqt import QRangeSlider
from utiles import nmToRGB, calcule_true_rgb_opti, calcule_rgb_3slid, calcule_rgb_plage, calcule_true_gray_opti

import os
import spectral as sp
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from qtpy.QtCore import Qt



# Désactiver le mode interactif de matplotlib
plt.ioff()


class Image_Mode_Slider(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.wavelength = None
        self.img_data = None    
        self.file_path = None
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Écrivez ici une description ou un commentaire...")
        self.text_edit.setStyleSheet("background-color: #3A3A3A; color: white; font-size: 14px; padding: 5px; border-radius : 5px")
        self.file_path = None
        self.setStyleSheet("background-color: #2E2E2E;")
        self.text = "Aucun commentaire effectué"

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
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI


    def update_slider_text(self):
        wavelenght = self.slider.value()
        self.label.setText(f"Longueur d'onde : {self.wavelength[wavelenght]} nm")


    def update_image(self):
        idx_wavelength = self.slider.value()
        # Switch-like behavior pour appliquer le bon cmap
        selected_mode = self.mode_combo.currentText()

        # Créer le titre dynamique
        title = f"Image reconstituée en mode {selected_mode} à la longueur d'onde {self.wavelength[idx_wavelength]} nm"
        self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre au-dessus de l'image

        if selected_mode == "RGB":
            img_data = calcule_true_rgb_opti(idx_wavelength, self.open_file)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en couleur
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Gris":
            img_data = calcule_true_gray_opti(idx_wavelength, self.open_file, self.wavelength)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array, cmap='gray')  # Affichage en niveaux de gris
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Couleur":
            img_data = calcule_true_gray_opti(idx_wavelength, self.open_file)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en niveaux de gris            self.Img_ax.axis('off')
            self.canvas.draw()

    def load_file(self, file_path, wavelength, data_img):
        self.wavelength = wavelength
        self.file_path = file_path
        self.img_data = data_img
        self.open_file = sp.open_image(self.file_path)
        # self.file_path = sp.open_image(os.path.basename(self.file_path))
        # self.img_data = self.file_path.load()  # Charger en tant que tableau NumPy
        # self.metadata = self.file_path.metadata  # Récupérer les métadonnées
        self.left_label = QLabel(f"{self.wavelength[0]} nm")
        self.right_label = QLabel(f"{self.wevelength[-1]} nm")
        # self.slider.setRange(float(self.wavelength[0]), float(self.wavelength[-1]))
        self.slider.setRange(0, len(self.wavelength)-1)

    def commenter(self):
          self.text, ok = QInputDialog.getMultiLineText(self, "Ajouter un commentaire", "commentaire destiné à la sauvegarde globale", "")

