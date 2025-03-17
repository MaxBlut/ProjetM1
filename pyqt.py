import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout, QTabWidget, QPushButton, QComboBox, QFrame
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QFont
import main as m
import spectral as sp

# Désactiver le mode interactif de matplotlib
plt.ioff()

class MatplotlibImage(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.setStyleSheet("background-color: #2E2E2E;")
        self.figure, self.Img_ax = plt.subplots(figsize=(10, 10), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.figure.patch.set_facecolor('#2E2E2E')

        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(402, 998)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(2)
        self.slider.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        self.slider.valueChanged.connect(self.update_slider_text)

        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Longueur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)

        self.left_label = QLabel("402 nm")
        self.left_label.setStyleSheet("color: white; font-size: 20px;")
        self.right_label = QLabel("998 nm")
        self.right_label.setStyleSheet("color: white; font-size: 20px;")

        # Création d'un menu déroulant pour sélectionner le mode d'affichage
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Couleur")
        self.mode_combo.addItem("Gris")
        self.mode_combo.addItem("RGB")
        self.mode_combo.currentIndexChanged.connect(self.update_image)

        layout = QVBoxLayout()
        layout.addWidget(self.mode_combo)  # Ajout du menu déroulant
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.right_label)
        layout.addLayout(slider_layout)
        layout.addWidget(self.label)
        self.setLayout(layout)

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
            img_data = m.calcule_true_rgb_opti(wavelength)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en couleur
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Gris":
            img_data = m.calcule_true_gray_opti(wavelength)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array, cmap='gray')  # Affichage en niveaux de gris
            self.Img_ax.axis('off')
            self.canvas.draw()

        elif selected_mode == "Couleur":
            img_data = m.calcule_true_gray_opti(wavelength)
            
            img_array = np.array(img_data, dtype=np.uint8)
            self.Img_ax.imshow(img_array)  # Affichage en niveaux de gris            self.Img_ax.axis('off')
            self.canvas.draw()

class MatplotlibImage_DoubleCurseur2(QWidget):
    def __init__(self, RGB_img):
        super().__init__()
        self.img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale
        if self.img is None or len(self.img.shape) != 3:
            print("Erreur : L'image hyperspectrale n'a pas été chargée correctement ou a une forme invalide.")
        self.setStyleSheet("background-color: #2E2E2E;")
        self.figure, self.Img_ax = plt.subplots(figsize=(10, 10), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.Img_ax.set_position([0, 0, 1, 1])
        self.figure.patch.set_facecolor('#2E2E2E')

        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: #AAB7B8; color: white; border-radius: 5px;")
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)

        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_min.setRange(402, 998)
        self.slider_min.setTickPosition(QSlider.TicksBelow)
        self.slider_min.setTickInterval(2)
        self.slider_min.setSingleStep(2)
        self.slider_min.valueChanged.connect(self.update_slid_text)
        self.slider_min.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased

        self.slider_max = QSlider(Qt.Horizontal)
        self.slider_max.setRange(402, 998)
        self.slider_max.setTickPosition(QSlider.TicksBelow)
        self.slider_max.setTickInterval(2)
        self.slider_max.setSingleStep(2)
        self.slider_max.valueChanged.connect(self.update_slid_text)
        self.slider_max.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased

        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Longueur d'onde : 0 nm")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 30px;")
        self.label.setFont(font)

        self.left_label = QLabel("402 nm")
        self.left_label.setStyleSheet("color: white; font-size: 20px;")
        self.right_label = QLabel("998 nm")
        self.right_label.setStyleSheet("color: white; font-size: 20px;")

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.left_label)
        slider_layout.addWidget(self.slider_min)
        slider_layout.addWidget(self.slider_max)
        slider_layout.addWidget(self.right_label)
        layout.addLayout(slider_layout)
        layout.addWidget(self.label)
        self.setLayout(layout)

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
        self.slider_min.sliderReleased.connect(self.update_spectre)

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
        self.spectrum_figure, self.spectrum_ax = plt.subplots(figsize=(5, 5), tight_layout=True)
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        # Calcul initial du spectre global
        self.spectrum_x = np.array([i for i in range(self.img.shape[2])])  # Longueurs d'onde (indices de bandes)

        self.img_s = np.array(self.img.load())  # ✅ Convertit en numpy.ndarray

        print(f"Type après .load(): {type(self.img)}")
        print(f"Shape après .load(): {self.img.shape}")  # Doit être (608, 968, 299)
        self.spectrum_y = np.mean(self.img_s, axis=(0, 1))  # Moyenne des pixels par bande


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
        mask = (self.spectrum_x >= wl_min) & (self.spectrum_x <= wl_max)
        print(f"spectrum_x: {self.spectrum_x}")
        print(f"spectrum_y: {self.spectrum_y}")
        print(f"mask: {mask}")

        self.spectrum_ax.clear()
        self.spectrum_ax.plot(self.spectrum_x[mask], self.spectrum_y[mask], color='cyan')
        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='white')
        self.spectrum_ax.set_ylabel("Intensité", color='white')
        self.spectrum_ax.set_facecolor("#1E1E1E")
        self.spectrum_ax.tick_params(axis='x', colors='white')
        self.spectrum_ax.tick_params(axis='y', colors='white')
        self.spectrum_canvas.draw()
        
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

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "Visualisation")
        self.tabs.addTab(self.tab2, "Onglet Vide")



        layout = QHBoxLayout()
        # layout.addWidget(self.matplotlib_widget_gris)
        layout.addWidget(self.matplotlib_widget_rgb)
        self.tab1.setLayout(layout)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.matplotlib_widget_double)
        self.tab2.setLayout(layout2)

        self.setCentralWidget(self.tabs)



if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
