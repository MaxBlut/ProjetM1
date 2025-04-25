from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QSizePolicy,  QFileDialog, QTextEdit
from PySide6.QtCore import Signal, QObject

import os
import spectral as sp

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import io
from PIL import Image
from reportlab.lib.utils import ImageReader

import numpy as np

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

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Écrivez ici une description ou un commentaire...")
        self.file_path = None

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_all_as_pdf)

        self.save_button.setMinimumWidth(200)
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        

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
        

        commentaires = []
        for widget in self.matplotlib_widgets :
            if hasattr(widget, 'commentaire') and widget.commentaire:
                # Vérifier si le widget a bien un attribut 'text'
                # print(f"Commentaire du widget {widget} : {widget.commentaire}")
                commentaires.append(widget.commentaire)
            else:
                commentaires.append("")
        # Create an in-memory bytes buffer
        buf = io.BytesIO()
        for i, widget in enumerate(self.matplotlib_widgets):
            
            y_pos = 0
            if hasattr(widget, 'figure'):  # Vérifier si le widget a bien une figure Matplotlib
                buf.seek(0)
                # Draw the figure and save it to the buffer
                widget.figure.canvas.draw()
                widget.figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                y_pos += save_img(buf, pdf_canvas, y_pos)  # Enregistrer l'image dans le PDF
                
                
            if hasattr(widget, 'SceneCanvas') and widget.SceneCanvas:
                buf.seek(0)
                # Render the SceneCanvas
                img_data = widget.SceneCanvas.render()  # shape: (H, W, 4)
                h, w, _ = img_data.shape


                rgb = img_data[:, :, :3]
                non_empty_mask = np.any(rgb < 250, axis=2)  # ignore nearly white

                coords = np.argwhere(non_empty_mask)
                if coords.size == 0:
                    cropped_img = Image.fromarray(img_data)  # fallback
                else:
                    y_min, x_min = coords.min(axis=0)
                    y_max, x_max = coords.max(axis=0) + 1

                    # Crop using array slicing
                    cropped_array = img_data[y_min:y_max, x_min:x_max, :]
                    cropped_img = Image.fromarray(cropped_array.astype(np.uint8))

                print(cropped_img.size)
                print((h, w))
                cropped_img.save(buf, format='png')
                y_pos += save_img(buf, pdf_canvas, y_pos)  # Enregistrer l'image dans le PDF

            for line in commentaires[i].split("\n"):
                pdf_canvas.drawString(50, y_pos, line)
                y_pos -= 15
            pdf_canvas.showPage()  # Nouvelle page pour chaque image

        pdf_canvas.save()
        print(f"PDF enregistré à : {file_path}")





    def import_file(self):
        options = QFileDialog.Options()
        self.file_path_noload, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier HDR", "", "HDR Files (*.hdr)", options=options)

        if not self.file_path_noload:  # Vérifie si un fichier a été sélectionné
            print("Aucun fichier sélectionné.")
            return
        self.fichier_selec.setText("Chargement en cours, veuillez patienter...")  # Afficher le chemin dans l'UI
        QApplication.processEvents() 

        self.fichier_selec.setText(os.path.basename(self.file_path_noload))  # Afficher le chemin dans l'UI

        self.img = sp.open_image(self.file_path_noload)

        self.data_img = self.img.load()  # Charger en tant que tableau NumPy
        if 'wavelength' in self.img.metadata:
            self.wavelength = self.img.metadata['wavelength']
        elif "Wavelength" in self.img.metadata:
            self.wavelength = self.img.metadata['Wavelength']
        self.wavelength = [float(i) for i in self.wavelength]





def save_img(buf, pdf_canvas, offstet=0):
    page_width, page_height = A4
    # Rewind the buffer's cursor to the beginning
    buf.seek(0)
    # Open the image directly from the buffer using PIL
    img = Image.open(buf)
    img_width, img_height = img.size
    # scale = min(page_width / img_width, (page_height - 100) / img_height)
    scale = page_width / img_width
    new_width = img_width * scale
    new_height = img_height * scale

    x_offset = (page_width - new_width) / 2
    y_offset = page_height - new_height - 50 - offstet

    img_reader = ImageReader(buf)
    pdf_canvas.drawImage(img_reader, x_offset, y_offset, width=new_width, height=new_height)
    # Ajouter le commentaire sous l'image
    pdf_canvas.setFont("Helvetica", 12)
    y_pos = y_offset - 80
    return y_pos 




class SignalEmitter(QObject):
    fichier_importe = Signal(str)  # Signal émis lors de l'importation d'un fichier