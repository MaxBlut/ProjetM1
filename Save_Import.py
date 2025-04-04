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
        for i in range(len(self.matplotlib_widgets)) :
            commentaires.append(self.matplotlib_widgets[i].text)

        for i, widget in enumerate(self.matplotlib_widgets):
            if hasattr(widget, 'figure'):  # Vérifier si le widget a bien une figure Matplotlib
                temp_img_path = f"temp_image_{i}.png"  # Nom unique pour chaque figure
                widget.figure.canvas.draw()  # Forcer le dessin de la figure avant de la sauvegarder
                widget.figure.savefig(temp_img_path, dpi=300, bbox_inches='tight')

                img = Image.open(temp_img_path)
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

        self.img = sp.open_image(os.path.basename(self.file_path_noload))
        self.data_img = self.file_path.load()  # Charger en tant que tableau NumPy
        if 'wavelength' in self.img.metadata:
            self.wavelength = self.img.metadata['wavelength']
        elif "Wavelength" in self.img.metadata:
            self.wavelength = self.img.metadata['Wavelength']
    
    def get_fichier(self):
        if self.file_path_noload is None:
            return None
        else:
            return self.file_path_noload


class SignalEmitter(QObject):
    fichier_importe = Signal(str)  # Signal émis lors de l'importation d'un fichier