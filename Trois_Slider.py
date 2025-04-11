import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QFont

from CustomElement import CommentButton

from qtpy.QtCore import Qt



class Trois_Slider(QWidget):
    def __init__(self):
        super().__init__()
        self.variable_init()
        self.ui_init()


    def variable_init(self):
        self.file_path = None
        self.img_data = None
        self.wavelength = None
        self.commentaire = None


    def ui_init(self):
        
        self.figure, (self.Img_ax, self.spectrum_ax) = plt.subplots(1, 2,figsize=(15, 10), gridspec_kw={'width_ratios': [1, 1]})
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.canvas = FigureCanvas(self.figure)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # self.Img_ax.set_position([0, 0, 0.6, 1])  # Image sur 60% de la largeur
        self.Img_ax.axis('off')
        # self.spectrum_ax.set_position([0.65, 0.1, 0.35, 0.8])  # Spectre sur 40% avec un petit décalage
        self.canvas.mpl_connect('button_press_event', self.on_click)

        toolbar = NavigationToolbar(self.canvas, self)
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
        self.slid_r.actionTriggered.connect(self.handle_slider_action)

        self.slid_g = QSlider(Qt.Horizontal)
        self.slid_g.setRange(0,0)
        self.slid_g.setTickPosition(QSlider.TicksBelow)
        self.slid_g.setTickInterval(2)
        self.slid_g.setSingleStep(2)
        self.slid_g.valueChanged.connect(self.update_slid_text)
        self.slid_g.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased
        self.slid_g.actionTriggered.connect(self.handle_slider_action)

        self.slid_b = QSlider(Qt.Horizontal)
        self.slid_b.setRange(0, 0)
        self.slid_b.setTickPosition(QSlider.TicksBelow)
        self.slid_b.setTickInterval(2)
        self.slid_b.setSingleStep(2)
        self.slid_b.valueChanged.connect(self.update_slid_text)
        self.slid_b.sliderReleased.connect(self.update_image)  # Connecter à sliderReleased$
        self.slid_b.actionTriggered.connect(self.handle_slider_action)




        comment_button = CommentButton(self)


        # Création des labels
        self.r_label = QLabel("R")
        self.g_label = QLabel("G")
        self.b_label = QLabel("B")



        # LABELS AU DSSUS --------------------------------
        self.value_r = QLabel(" veuillez analyser le fichier")
        self.value_r.setAlignment(Qt.AlignCenter)

        self.value_g = QLabel("")
        self.value_g.setAlignment(Qt.AlignCenter)

        self.value_b = QLabel("")
        self.value_b.setAlignment(Qt.AlignCenter)


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

        # LABELS---------------------------------------------
        font = QFont("Verdana", 20, QFont.Bold)
        self.label = QLabel("Choisir des longueurs d'onde pour les canaux R, G, B")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)

       
        # LAYOUTS---------------------------------------------
        import_layout = QHBoxLayout()
        import_layout.addWidget(toolbar)
        import_layout.addWidget(comment_button)
        

        import_layout.setAlignment(comment_button, Qt.AlignRight)

        img_layout = QVBoxLayout()
        img_layout.addLayout(import_layout)
        img_layout.addWidget(self.canvas)
        img_layout.addLayout(slider_layout)
        img_layout.addWidget(self.label)
        img_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges autour du layout

        # Création de l'affichage du spectre

        self.spectrum_ax.set_xlabel("Longueur d'onde (nm)", color='white')
        self.spectrum_ax.set_ylabel("Intensité", color='white')
        self.spectrum_ax.set_xlim(0, 1)
        self.spectrum_ax.tick_params(axis='x', colors='white')
        self.spectrum_ax.tick_params(axis='y', colors='white')
        # Graphique vide au départ (sans données)
        self.spectrum_ax.bar([], [], color=['red', 'green', 'blue'])  # Barres vides
        self.spectrum_ax.set_title("Réflectance en fonction de la longueur d'onde")
        self.canvas.draw()

        self.figure.tight_layout()
        self.setLayout(img_layout)


    def update_slid_text(self):
        # Récupérer les valeurs des sliders
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()

        # Mettre à jour le texte des labels
        self.value_r.setText(f"{self.wavelength[wl_r]} nm")
        self.value_g.setText(f"{self.wavelength[wl_g]} nm")
        self.value_b.setText(f"{self.wavelength[wl_b]} nm")

        # Afficher la valeur des sliders sous forme de tooltip
        self.slid_r.setToolTip(f"{self.wavelength[wl_r]} nm")
        self.slid_g.setToolTip(f"{self.wavelength[wl_g]} nm")
        self.slid_b.setToolTip(f"{self.wavelength[wl_b]} nm")


    def update_image(self):

        self.figure.tight_layout()
        wl_r = self.slid_r.value()
        wl_g = self.slid_g.value()
        wl_b = self.slid_b.value()
        # title = f"Image reconstituée interpretant la longueur d'onde R comme {self.wavelength[wl_r]} nm, G: {self.wavelength[wl_g]} nm, B: {self.wavelength[wl_b]} nm"
        # self.Img_ax.set_title(title, fontsize=16, color='white', pad=20)  # Ajoute le titre
        self.Img_ax.set_title("Image RGB reconstituée")
        self.imgopt.set_data(self.img_data[:, :, (wl_r, wl_g, wl_b)])
        self.canvas.draw_idle()



    def load_file(self, file_path, wavelength, data_img):
        self.wavelength = wavelength
        self.file_path = file_path
        self.img_data = data_img

        self.imgopt = self.Img_ax.imshow(self.img_data[:,:,(0,1,2)])
        self.Img_ax.axis('off')

        # Charger le fichier HDR

        self.slid_r.setRange(0, len(self.wavelength)-1)
        self.slid_g.setRange(0, len(self.wavelength)-1)
        self.slid_b.setRange(0, len(self.wavelength)-1)
        self.update_image()
        # self.spectrum_ax.set_xlim(float(self.wavelength[0]), float(self.wavelength[-1]))
        self.figure.tight_layout()

        self.value_r.setText(" Choisissez une longueur d'onde")
        self.value_g.setText(" ")
        self.value_b.setText(" ")

    

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
        if self.img_data is None:
            print("Aucune image hyperspectrale chargée.")
            return

        if event.inaxes != self.Img_ax:
            return

        x, y = int(event.xdata), int(event.ydata)

        # Récupération des longueurs d'onde choisies
        wavelengths = [self.wavelength[self.slid_r.value()],self.wavelength[self.slid_g.value()], self.wavelength[self.slid_b.value()]]
        reflectance_values = []

        # Conversion des longueurs d'onde en indices de bande
        wavelengths_available = np.array(self.wavelength, dtype=float)
        for wl in wavelengths:
            idx = np.abs(wavelengths_available - float(wl)).argmin()
            reflectance_values.append(self.img_data[y, x, idx])

        # Mise à jour de l'affichage
        self.update_spectrum(wavelengths, reflectance_values)

    def handle_slider_action(self, action):
        if action ==3 or action == 4:  # 3 => jump-by-10-ticks right , 4 = jump-by-10-ticks left 
            self.update_image()


