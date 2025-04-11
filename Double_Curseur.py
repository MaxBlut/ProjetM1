import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from CustomElement import CustomWidgetRangeSlider, CommentButton
from utiles import calcule_rgb_plage
import os
import spectral as sp

from PySide6.QtCore import Signal


class Double_Curseur(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.wavelength = None
        self.img_data = None
        self.commentaire = None

        # Création d'une figure avec 2 axes : 1 pour l'image et 1 pour le spectre
        self.figure, (self.Img_ax, self.spectrum_ax) = plt.subplots(1, 2, figsize=(15, 10), gridspec_kw={'width_ratios': [1, 1]})
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        # self.Img_ax.set_position([0, 0, 0.5, 1])  # Image occupe 60% de la largeur
        # self.spectrum_ax.set_position([0.6, 0.1, 0.5, 0.8])  # Augmenter la largeur
        self.figure.tight_layout()  # Applique à toute la figure


        toolbar_layout = QHBoxLayout()
        # Toolbar pour la navigation
        toolbar = NavigationToolbar(self.canvas, self)
        for action in toolbar.actions():
            if action.text() in ["Home", "Customize"]:
                toolbar.removeAction(action)
        toolbar_layout.addWidget(toolbar)

        button_com = CommentButton(self)
        toolbar_layout.addWidget(button_com)

        # Slider de contrôle pour les longueurs d'onde
        self.slider_widget = CustomWidgetRangeSlider()
        self.slider_widget.range_slider.sliderReleased.connect(self.update_image)
        self.slider_widget.range_slider.sliderReleased.connect(self.update_spectre)
        self.slider_widget.range_slider.valueChanged.connect(self.slider_widget.update_label)
      
        # Layout pour les sliders et le bouton d'importation
        import_layout = QHBoxLayout()

        img_layout = QVBoxLayout()
        img_layout.addLayout(toolbar_layout)
        img_layout.addLayout(import_layout)
        img_layout.addWidget(self.canvas)
        img_layout.addWidget(self.slider_widget)

        self.setLayout(img_layout)

        # Affichage de l'image initiale
        self.Img_ax.axis('off')
        self.spectrum_ax.axis('off')
        self.canvas.draw()


    def update_file(self, path):
        self.file_path = path
        self.fichier_selec.setText(os.path.basename(path))  # Afficher le nom du fichier dans l'UI


    def update_image(self):
        self.Img_ax.clear()
        idx_min, idx_max = self.slider_widget.range_slider.value()
        img_data = calcule_rgb_plage(self.img_data, self.wavelength, idx_min, idx_max)
        img_array = np.array(img_data, dtype=np.uint8)
        title = f"Image reconstituée entre {self.wavelength[idx_min]} nm et {self.wavelength[idx_max]} nm"
        self.Img_ax.imshow(img_array)
        self.Img_ax.set_title(title, fontsize=16, color='black', pad=20)  # Ajoute le titre

        self.Img_ax.axis('off')
        self.canvas.draw()


    def update_spectre(self):
        wl_min, wl_max = self.slider_widget.range_slider.value()
        self.spectrum_ax.clear()

        mean = np.mean(self.img_data[:,:,wl_min:wl_max], axis=(0,1))
        self.spectrum_ax.plot(self.wavelength[wl_min:wl_max], mean, color='cyan')

        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='black')
        self.spectrum_ax.set_ylabel("Intensité", color='black')
        self.spectrum_ax.set_xlim(self.wavelength[wl_min], self.wavelength[wl_max])
        self.spectrum_ax.set_xticks([self.wavelength[wl_min], self.wavelength[wl_max]])
        self.spectrum_ax.set_xticklabels([f"{float(self.wavelength[wl_min]):.0f}", f"{float(self.wavelength[wl_max]):.0f}"])
        self.spectrum_ax.tick_params(axis='x', colors='black')
        self.spectrum_ax.tick_params(axis='y', colors='black')
        self.figure.tight_layout()
        self.canvas.draw()


    def load_file(self, file_path, wavelength, data_img):
        self.wavelength = wavelength
        self.file_path = file_path
        self.img_data = data_img

        self.slider_widget.setWavelenghts(self.wavelength)
       
        self.update_image()
        self.update_spectre()

    

















class MyWindow(QMainWindow):
    # Define a signal that emits new width & height
    
    resized = Signal(int, int)
    def __init__(self):
        super().__init__()
        # Create an instance of CustomWidget and pass the resize signal
        self.widget = Double_Curseur()
        self.file_path ="D:/MAXIME/cours/4eme_annee/Projet_M1/wetransfer_data_m1_nantes_2025-03-25_1524/Data_M1_Nantes/VNIR(400-1000nm)/E2_Adm_On_J0_Pl1_F1_2.bil.hdr"
        img = sp.open_image(self.file_path)
        self.data_img = img.load()
        if 'wavelength' in img.metadata:
            self.wavelengths = img.metadata['wavelength']
        elif "Wavelength" in img.metadata:
            self.wavelengths = img.metadata['Wavelength']
        self.wavelengths = [float(i) for i in self.wavelengths]
        self.setCentralWidget(self.widget)

        self.resized.connect(lambda : self.widget.load_file(self.file_path, self.wavelengths, self.data_img))



    def resizeEvent(self, event):
        """ Emits the signal when the window is resized """
        new_width = self.width()
        new_height = self.height()
        self.resized.emit(new_width, new_height) 
        super().resizeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())