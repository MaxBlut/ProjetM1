import sys
import main as m
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSpacerItem, QSizePolicy

# Désactiver le mode interactif pour éviter que Matplotlib ouvre des fenêtres

plt.ioff()

class MatplotlibImage_RGB(QWidget):
    def __init__(self, RGB_img):
        super().__init__()

        self.setStyleSheet("background-color: #2E2E2E;")

        # Création de la figure et du canvas
        self.figure, self.Img_ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")  
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:  # "Customize" correspond au bouton statistique
                toolbar.removeAction(action)
        # Créer un QSlider (curseur horizontal ou vertical)
        self.slider = QSlider(Qt.Horizontal)  # Qt.Vertical pour un curseur vertical
        self.slider.setRange(402, 998)  # Plage du curseur basée sur la largeur de l'image
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(2)    # Pas de 2 pour chaque "clic" ou déplacement

        # Ajuster la largeur du slider pour qu'il corresponde à la largeur de l'image
        self.slider.setFixedWidth(self.width() - 50)  # Laisser un peu d'espace autour
        font = QFont("Verdana", 20, QFont.Bold)  # Choisir la police Arial, taille 20, en gras

        # ECHELLE MIDDLE
        self.label = QLabel(f"Longeur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white; border-radius: 15px; font-size: 30px;")
        self.label.setFixedHeight(30)  # Ajuster la hauteur du label à 30px par exemple
        self.label.setFont(font)  # Appliquer la police au label


        # ECHELLE SLIDER GAUCHE
        self.left_label = QLabel("402 nm")
        self.left_label.setAlignment(Qt.AlignLeft)
        self.left_label.setStyleSheet("background-color: black; color: white; font-size: 20px; border-radius: 15px;")
        self.left_label.setFont(font)  # Appliquer la même police

        # ECHELLE SLIDER DROITE
        self.right_label = QLabel("998 nm")
        self.right_label.setAlignment(Qt.AlignRight)
        self.right_label.setStyleSheet("background-color: black; color: white; font-size: 20px; border-radius: 15px;")
        self.right_label.setFont(font)  # Appliquer la même police



        # Connecter le signal de changement de valeur du slider à la méthode de mise à jour
        self.slider.valueChanged.connect(self.update_image)

        # Layout principal
        layout = QVBoxLayout()

        # Ajouter le toolbar et l'image
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        # Créer un layout horizontal pour centrer le slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.right_label)


        # Ajouter le slider et le label sous l'image
        layout.addLayout(slider_layout)  # Ajouter le layout horizontal du slider
        layout.addWidget(self.label)  # Ajouter le label

        self.setLayout(layout)

        # Affichage de l'image dans PyQt uniquement
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

        # Imposer une taille fixe à la fenêtre (si nécessaire)
        self.setFixedSize(800, 600)  # Taille fixe de la fenêtre

        self.update_image()

    def update_image(self):
        """Met à jour l'image en fonction de la valeur actuelle du curseur."""
        # Obtenir la valeur du slider
        wavelength = self.slider.value()
        self.label.setText(f"Longeur d'onde : {wavelength} nm")

        # Passer la valeur du slider à la méthode calcule_true_rgb
        img_data = m.calcule_true_rgb_opti(wavelength)

        # Convertir l'image en tableau numpy
        img_array = np.array(img_data, dtype=np.uint8)

        # Effacer l'ancienne image
        self.Img_ax.clear()

        # Afficher la nouvelle image
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def get_slider_value(self):
        """Retourne la valeur actuelle du slider."""
        return self.slider.value()


class MatplotlibImage_Gris(QWidget):
    def __init__(self, RGB_img):
        super().__init__()

        self.setStyleSheet("background-color: #2E2E2E;")

        # Création de la figure et du canvas
        self.figure, self.Img_ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")  
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:  # "Customize" correspond au bouton statistique
                toolbar.removeAction(action)
        # Créer un QSlider (curseur horizontal ou vertical)
        self.slider = QSlider(Qt.Horizontal)  # Qt.Vertical pour un curseur vertical
        self.slider.setRange(402, 998)  # Plage du curseur basée sur la largeur de l'image
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(2)    # Pas de 2 pour chaque "clic" ou déplacement

        # Ajuster la largeur du slider pour qu'il corresponde à la largeur de l'image
        self.slider.setFixedWidth(self.width() - 50)  # Laisser un peu d'espace autour
        font = QFont("Verdana", 20, QFont.Bold)  # Choisir la police Arial, taille 20, en gras

        # ECHELLE MIDDLE
        self.label = QLabel(f"Longeur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white; border-radius: 15px; font-size: 30px;")
        self.label.setFixedHeight(30)  # Ajuster la hauteur du label à 30px par exemple
        self.label.setFont(font)  # Appliquer la police au label


        # ECHELLE SLIDER GAUCHE
        self.left_label = QLabel("402 nm")
        self.left_label.setAlignment(Qt.AlignLeft)
        self.left_label.setStyleSheet("background-color: black; color: white; font-size: 20px; border-radius: 15px;")
        self.left_label.setFont(font)  # Appliquer la même police

        # ECHELLE SLIDER DROITE
        self.right_label = QLabel("998 nm")
        self.right_label.setAlignment(Qt.AlignRight)
        self.right_label.setStyleSheet("background-color: black; color: white; font-size: 20px; border-radius: 15px;")
        self.right_label.setFont(font)  # Appliquer la même police



        # Connecter le signal de changement de valeur du slider à la méthode de mise à jour
        self.slider.valueChanged.connect(self.update_image)

        # Layout principal
        layout = QVBoxLayout()

        # Ajouter le toolbar et l'image
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        # Créer un layout horizontal pour centrer le slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.right_label)


        # Ajouter le slider et le label sous l'image
        layout.addLayout(slider_layout)  # Ajouter le layout horizontal du slider
        layout.addWidget(self.label)  # Ajouter le label

        self.setLayout(layout)

        # Affichage de l'image dans PyQt uniquement
        self.Img_ax.imshow(RGB_img, cmap='gray')
        self.Img_ax.axis('off')
        self.canvas.draw()

        # Imposer une taille fixe à la fenêtre (si nécessaire)
        self.setFixedSize(800, 600)  # Taille fixe de la fenêtre

        self.update_image()

    def update_image(self):
        """Met à jour l'image en fonction de la valeur actuelle du curseur."""
        # Obtenir la valeur du slider
        wavelength = self.slider.value()
        self.label.setText(f"Longeur d'onde : {wavelength} nm")

        # Passer la valeur du slider à la méthode calcule_true_rgb
        img_data = m.calcule_true_gray_opti(wavelength)

        # Convertir l'image en tableau numpy
        img_array = np.array(img_data, dtype=np.uint8)

        # Effacer l'ancienne image
        self.Img_ax.clear()

        # Afficher la nouvelle image
        self.Img_ax.imshow(img_array)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def get_slider_value(self):
        """Retourne la valeur actuelle du slider."""
        return self.slider.value()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()
        self.setStyleSheet("background-color: #2E2E2E;")

        # Exemple d'image initiale (image noire de 100x100 pixels)
        initial_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Créer l'instance de MatplotlibImage avec l'image initiale
        self.matplotlib_widget_gris = MatplotlibImage_Gris(initial_image)
        self.matplotlib_widget = MatplotlibImage_RGB(initial_image)

        # Créer un layout horizontal pour afficher les deux widgets côte à côte
        main_layout = QHBoxLayout()

        # Ajouter les deux widgets à ce layout
        main_layout.addWidget(self.matplotlib_widget_gris)
        main_layout.addWidget(self.matplotlib_widget)

        # Créer un widget central pour contenir le layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Définir ce widget comme central
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:  
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
