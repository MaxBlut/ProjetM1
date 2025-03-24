import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QTabWidget, QPushButton, QComboBox, QSizePolicy,  QFileDialog, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QFont
#from qtrangeslider import QLabeledRangeSlider, QDoubleSlider
from superqt import QLabeledRangeSlider
import main as m
import spectral as sp

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

# Désactiver le mode interactif de matplotlib
plt.ioff()


class MatplotlibImage(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Écrivez ici une description ou un commentaire...")
        self.text_edit.setStyleSheet("background-color: #3A3A3A; color: white; font-size: 14px; padding: 5px;")
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
        self.import_button = QPushButton("Importer fichier")
        self.import_button.clicked.connect(self.import_file)



        
        self.fichier_selec = QLabel("{Aucun fichier sélectionné}")

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
        left_layout = QVBoxLayout()
        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)
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

        self.save_button = QPushButton("Sauvegarde")
        self.save_button.clicked.connect(self.save_as_pdf)

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



        right_layout = QVBoxLayout()
        right_layout.addStretch()  # Ajoute un espace flexible en haut
        right_layout.addWidget(self.choix_label)
        right_layout.addWidget(self.mode_combo)
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.save_button)
        # right_layout.addStretch()  # Ajoute un espace flexible en bas

        self.qlrs = QLabeledRangeSlider(Qt.Horizontal)
        self.qlrs.valueChanged.connect(lambda e: print("QLabeledRangeSlider valueChanged", e))
        self.qlrs.setValue((20, 60))
        right_layout.addWidget(self.qlrs)

        # Disposition globale : Image + contrôles à gauche | Mode combo & sauvegarde à droite
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_slider_text(self):
        wavelenght = self.slider.value()
        self.label.setText(f"Longueur d'onde : {wavelenght} nm")


    def update_image(self):
        wavelength = self.slider.value()
        # Switch-like behavior pour appliquer le bon cmap
        selected_mode = self.mode_combo.currentText()

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
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Importer un fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt)", options=options)
        self.fichier_selec.setText(self.file_path)
        self.file_path = sp.open_image(self.file_path)

    def save_as_pdf(self):
        if not self.file_path:
            print("Aucune image chargée.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer sous", "", "Fichier PDF (*.pdf)")
        if not file_path:
            return

        # Sauvegarde temporaire de l'image affichée par Matplotlib
        temp_img_path = "temp_image.png"
        self.figure.savefig(temp_img_path, dpi=300, bbox_inches='tight')  # Sauvegarde directe de la figure

        # Création du PDF
        pdf_canvas = canvas.Canvas(file_path, pagesize=A4)

        # Ajout de l'image au PDF
        img = Image.open(temp_img_path)
        img_width, img_height = img.size
        page_width, page_height = A4
        scale = min(page_width / img_width, (page_height - 100) / img_height)
        new_width = img_width * scale
        new_height = img_height * scale

        x_offset = (page_width - new_width) / 2
        y_offset = page_height - new_height - 50
        pdf_canvas.drawImage(temp_img_path, x_offset, y_offset, width=new_width, height=new_height)

        # Sauvegarde du texte sur une autre page
        pdf_canvas.showPage()
        text = self.text_edit.toPlainText()
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(50, page_height - 50, "Commentaire de l'utilisateur :")

        y_pos = page_height - 80
        for line in text.split("\n"):
            pdf_canvas.drawString(50, y_pos, line)
            y_pos -= 20

        pdf_canvas.save()
        print(f"PDF enregistré à : {file_path}")


class MatplotlibImage_DoubleCurseur(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale
        if self.img is None or len(self.img.shape) != 3:
            raise ValueError("L'image hyperspectrale n'a pas été chargée correctement !")
        self.setStyleSheet("background-color: #2E2E2E;")
        
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

        #SLIDER MIN ET MAX
        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_min.setRange(402, 998)
        self.slider_min.setTickPosition(QSlider.TicksBelow)
        self.slider_min.setTickInterval(2)
        self.slider_min.setSingleStep(2)
        self.slider_min.valueChanged.connect(self.update_slid_text)
        self.slider_min.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        self.slider_min.sliderReleased.connect(self.update_spectre)
        
        self.slider_max = QSlider(Qt.Horizontal)
        self.slider_max.setRange(402, 998)
        self.slider_max.setTickPosition(QSlider.TicksBelow)
        self.slider_max.setTickInterval(2)
        self.slider_max.setSingleStep(2)
        self.slider_max.valueChanged.connect(self.update_slid_text)
        self.slider_max.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        self.slider_max.sliderReleased.connect(self.update_spectre)

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

        #LAYOUTS---------------------------------------------
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.slider_min)
        slider_layout.addWidget(self.slider_max)

        img_layout = QVBoxLayout()
        img_layout.addWidget(toolbar)
        img_layout.addWidget(self.canvas)
        img_layout.addLayout(slider_layout)
        img_layout.addWidget(self.label)

        #SPECTRE---------------------------------------------
        self.spectrum_figure, self.spectrum_ax = plt.subplots(figsize=(5, 5))
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        self.spectrum_ax.set_ylabel("Intensité", color='black')
        self.spectrum_ax.set_xlim(402, 998)
        self.spectrum_ax.tick_params(axis='x', colors='black')
        self.spectrum_ax.tick_params(axis='y', colors='black')
        # Calcul initial du spectre global
        self.spectrum_x = self.img.metadata['wavelength']
        self.spectrum_x = np.array(self.spectrum_x)
        self.spectrum_x = self.spectrum_x.astype(float)

        self.img_s = np.array(self.img.load())  # ✅ Convertit en numpy.ndarray

        print(f"Type après .load(): {type(self.img_s)}")
        print(f"Shape après .load(): {self.img_s.shape}")  # Doit être (608, 968, 299)
        self.spectrum_y = np.mean(self.img_s, axis=(0,1))  # Moyenne des pixels par bande
        self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')


        main_layout = QHBoxLayout()
        main_layout.addLayout(img_layout, 1)
        main_layout.addWidget(self.spectrum_canvas, 1)

        self.setLayout(main_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_slid_text(self):
        wl_min = self.slider_min.value()
        wl_max = self.slider_max.value()
        self.label.setText(f"{wl_min} nm à {wl_max} nm")

    def update_image(self):
        wl_min = self.slider_min.value()
        wl_max = self.slider_max.value()
        img_data = m.calcule_rgb_plage(self.img, wl_min, wl_max)
        img_array = np.array(img_data, dtype=np.uint8)
        self.Img_ax.clear()
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()
    
    def update_spectre(self):
        wl_min = self.slider_min.value()
        wl_max = self.slider_max.value()
        k_min = round((wl_min - 400) / 2)
        k_max = round((wl_max - 400) / 2)
        if wl_min < wl_max: 
            #mask = (self.spectrum_x >= wl_min) & (self.spectrum_x <= wl_max)
            #self.spectrum_ax.plot(self.spectrum_x[mask], self.spectrum_y[mask], color='cyan')
            self.spectrum_ax.plot(self.spectrum_x[k_min:k_max], self.spectrum_y[k_min:k_max], color='cyan')
                       

            #self.spectrum_ax.plot(self.spectrum_x[mask], self.spectrum_y[mask], color='cyan')
            self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
            self.spectrum_ax.set_ylabel("Intensité", color='black')
            self.spectrum_ax.set_xlim(wl_min, wl_max)
            self.spectrum_ax.tick_params(axis='x', colors='black')
            self.spectrum_ax.tick_params(axis='y', colors='black')
            self.spectrum_figure.tight_layout()
            self.spectrum_canvas.draw()
        
class MatplotlibImage_3slid(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.file_path = None
        # self.img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale
        # if self.img is None or len(self.img.shape) != 3:
        #     raise ValueError("L'image hyperspectrale n'a pas été chargée correctement !")
        self.setStyleSheet("background-color: #2E2E2E;")
        
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

        #SLIDER MIN ET MAX
        self.slid_r = QSlider(Qt.Horizontal)
        self.slid_r.setRange(402, 998)
        self.slid_r.setTickPosition(QSlider.TicksBelow)
        self.slid_r.setTickInterval(2)
        self.slid_r.setSingleStep(2)
        self.slid_r.valueChanged.connect(self.update_slid_text)
        self.slid_r.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        # self.slid_r.sliderReleased.connect(self.update_spectre)
        
        self.slid_g = QSlider(Qt.Horizontal)
        self.slid_g.setRange(402, 998)
        self.slid_g.setTickPosition(QSlider.TicksBelow)
        self.slid_g.setTickInterval(2)
        self.slid_g.setSingleStep(2)
        self.slid_g.valueChanged.connect(self.update_slid_text)
        self.slid_g.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        # self.slid_g.sliderReleased.connect(self.update_spectre)

        self.slid_b = QSlider(Qt.Horizontal)
        self.slid_b.setRange(402, 998)
        self.slid_b.setTickPosition(QSlider.TicksBelow)
        self.slid_b.setTickInterval(2)
        self.slid_b.setSingleStep(2)
        self.slid_b.valueChanged.connect(self.update_slid_text)
        self.slid_b.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        # self.slid_b.sliderReleased.connect(self.update_spectre)

        #---------------- Bouton "Importer fichier" 
        self.import_button = QPushButton("Importer fichier")
        self.import_button.clicked.connect(self.import_file)
        self.fichier_selec = QLabel("{Aucun fichier sélectionné}")

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

        #LABELS---------------------------------------------
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Saisir des longeurs d'onde pour les canaux R, G, B")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)
        
        self.left_label = QLabel("402 nm")
        self.left_label.setStyleSheet("color: white; font-size: 20px;")
        self.right_label = QLabel("998 nm")
        self.right_label.setStyleSheet("color: white; font-size: 20px;")

        #LAYOUTS---------------------------------------------
        import_layout = QHBoxLayout()
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.fichier_selec)


        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.slid_r)
        slider_layout.addWidget(self.slid_g)
        slider_layout.addWidget(self.slid_b)

        img_layout = QVBoxLayout()
        img_layout.addLayout(import_layout)
        img_layout.addWidget(toolbar)
        img_layout.addWidget(self.canvas)
        img_layout.addLayout(slider_layout)
        img_layout.addWidget(self.label)

        # #SPECTRE---------------------------------------------
        # self.spectrum_figure, self.spectrum_ax = plt.subplots(figsize=(5, 5))
        # self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        # self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        # self.spectrum_ax.set_ylabel("Intensité", color='black')
        # self.spectrum_ax.set_xlim(402, 998)
        # self.spectrum_ax.tick_params(axis='x', colors='black')
        # self.spectrum_ax.tick_params(axis='y', colors='black')
        # # Calcul initial du spectre global
        # self.spectrum_x = self.img.metadata['wavelength']
        # self.spectrum_x = np.array(self.spectrum_x)
        # self.spectrum_x = self.spectrum_x.astype(float)

        # self.img_s = np.array(self.img.load())  # ✅ Convertit en numpy.ndarray

        # print(f"Type après .load(): {type(self.img_s)}")
        # print(f"Shape après .load(): {self.img_s.shape}")  # Doit être (608, 968, 299)
        # self.spectrum_y = np.mean(self.img_s, axis=(0,1))  # Moyenne des pixels par bande
        # self.spectrum_ax.plot(self.spectrum_x, self.spectrum_y, color='cyan')


        main_layout = QHBoxLayout()
        main_layout.addLayout(img_layout, 1)
        # main_layout.addWidget(self.spectrum_canvas, 1)

        self.setLayout(main_layout)
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_slid_text(self):
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()
        self.label.setText(f"Canal R :{wl_r} nm \n Canal G: {wl_g} nm \n Canal B: {wl_b} nm")

    def update_image(self):
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()
        img_data = m.calcule_rgb_3slid(wl_r, wl_g, wl_b, self.file_path)
        if img_data is None:
            print("Erreur : img_data est None")
            return  # ou autre traitement d'erreur
        img_array = np.array(img_data, dtype=np.uint8)
        self.Img_ax.clear()
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def import_file(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Importer un fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt)", options=options)
        self.fichier_selec.setText(self.file_path)
        self.file_path = sp.open_image(self.file_path)
    
    # def update_spectre(self):
    #     wl_min = self.slid_r.value()
    #     wl_max = self.slid_g.value()
    #     k_min = round((wl_min - 400) / 2)
    #     k_max = round((wl_max - 400) / 2)
    #     if wl_min < wl_max: 
    #         #mask = (self.spectrum_x >= wl_min) & (self.spectrum_x <= wl_max)
    #         #self.spectrum_ax.plot(self.spectrum_x[mask], self.spectrum_y[mask], color='cyan')
    #         self.spectrum_ax.plot(self.spectrum_x[k_min:k_max], self.spectrum_y[k_min:k_max], color='cyan')
                       

    #         #self.spectrum_ax.plot(self.spectrum_x[mask], self.spectrum_y[mask], color='cyan')
    #         self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
    #         self.spectrum_ax.set_ylabel("Intensité", color='black')
    #         self.spectrum_ax.set_xlim(wl_min, wl_max)
    #         self.spectrum_ax.tick_params(axis='x', colors='black')
    #         self.spectrum_ax.tick_params(axis='y', colors='black')
    #         self.spectrum_figure.tight_layout()
    #         self.spectrum_canvas.draw()
            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()
        self.setStyleSheet("background-color: #2E2E2E;")

        initial_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Image en couleur par défaut
        # self.matplotlib_widget_gris = MatplotlibImage_Gris(initial_image)
        self.matplotlib_widget_rgb = MatplotlibImage(initial_image)
        self.matplotlib_widget_double = MatplotlibImage_DoubleCurseur(initial_image)
        self.matplotlib_widget_3slid = MatplotlibImage_3slid(initial_image)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tabs.addTab(self.tab1, "WL unique")
        self.tabs.addTab(self.tab2, "Plage WL")
        self.tabs.addTab(self.tab3, "3 WL")

        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #3A3A3A;  /* Gris plus clair */
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
        # self.tabs.addTab(self.tab2, "Plage WL")
        # self.tabs.addTab(self.tab3, "3 WL")


        layout = QHBoxLayout()
        # layout.addWidget(self.matplotlib_widget_gris)
        layout.addWidget(self.matplotlib_widget_rgb)
        self.tab1.setLayout(layout)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.matplotlib_widget_double)
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(self.matplotlib_widget_3slid)
        self.tab3.setLayout(layout3)

        self.setCentralWidget(self.tabs)



if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    qlrs = QLabeledRangeSlider(Qt.Horizontal)
    qlrs.valueChanged.connect(lambda e: print("QLabeledRangeSlider valueChanged", e))
    qlrs.setValue((20, 60))
    qlrs.show()
    sys.exit(app.exec())
