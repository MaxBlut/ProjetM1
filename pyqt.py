import sys
import main as m
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# Désactiver le mode interactif pour éviter que Matplotlib ouvre des fenêtres

plt.ioff()

class MatplotlibImage(QWidget):
    def __init__(self, RGB_img):
        super().__init__()

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

        self.slider.setFixedWidth(self.width())  # Utiliser la largeur du widget pour le slider

        # Créer un QLabel pour afficher la valeur actuelle du curseur
        self.label = QLabel(f"Longeur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px; font-size: 30px;")
        self.label.setFixedHeight(30)  # Ajuster la hauteur du label à 30px par exemple

        self.slider.valueChanged.connect(self.update_label)

        # Layout principal
        layout = QVBoxLayout()

        # Ajouter le toolbar et l'image
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        # Créer un layout horizontal pour centrer le slider
        slider_layout = QHBoxLayout()
        slider_layout.addStretch()  # Pour centrer le slider
        slider_layout.addWidget(self.slider)
        slider_layout.addStretch()

        # Ajouter le slider et le label sous l'image
        layout.addLayout(slider_layout)  # Ajouter le layout horizontal du slider
        layout.addWidget(self.label)  # Ajouter le label

        self.setLayout(layout)

        # Affichage de l'image dans PyQt uniquement
        self.Img_ax.imshow(RGB_img)
        self.Img_ax.axis('off')
        self.canvas.draw()

    def update_label(self):
        """Met à jour le QLabel avec la valeur actuelle du curseur."""
        self.label.setText(f"Longeur d'onde : {self.slider.value()} nm")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()

        # Charger l'image depuis main.py
        img_data = m.calcule_true_rgb(550)
        if isinstance(img_data, int):  # Vérifier si l'image est invalide
            print("Erreur lors du chargement de l'image.")
            sys.exit()

        img_array = np.array(img_data, dtype=np.uint8)

        # Ajouter l'image Matplotlib dans l'interface PyQt
        self.matplotlib_widget = MatplotlibImage(img_array)
        self.setCentralWidget(self.matplotlib_widget)

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:  
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
