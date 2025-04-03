import spectral as sp
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from qtpy.QtCore import Qt
import signal
from superqt import QRangeSlider
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QLabel, QHBoxLayout
# Set the envi_support_nonlowercase_params to True to avoid an error message 
sp.settings.envi_support_nonlowercase_params = True


wlMin = 402
wlMax = 998
#reflectance_image = sp.open_image("feuille_250624_ref.hdr")


def nmToRGB(wavelength):
    # This function takes a wavelength value as an input and returns the corresponding RGB values
    # The RGB values are calculated using a piecewise function
    # The function is based on the work of Dan Bruton
    # https://academo.org/demos/wavelength-to-colour-relationship/

    red, green, blue = 0.0, 0.0, 0.0
    if((wavelength >= 380) and (wavelength<440)):
        red = -(wavelength - 440) / (440 - 380)
        green = 0.0
        blue = 1.0
    elif((wavelength >= 440) and (wavelength<490)):
        red = 0.0
        green = (wavelength - 440) / (490 - 440)
        blue = 1.0
    elif((wavelength >= 490) and (wavelength<510)):
        red = 0.0
        green = 1.0
        blue = -(wavelength - 510) / (510 - 490)
    elif((wavelength >= 510) and (wavelength<580)):
        red = (wavelength - 510) / (580 - 510)
        green = 1.0
        blue = 0.0
    elif((wavelength >= 580) and (wavelength<645)):
        red = 1.0
        green = -(wavelength - 645) / (645 - 580)
        blue = 0.0
    elif((wavelength >= 645) and (wavelength<781)):
        red = 1.0
        green = 0.0
        blue = 0.0
    else:
        red = 0.0
        green = 0.0
        blue = 0.0
    return red, green, blue
    

    
def on_close(event):
    print("La fenêtre a été fermée.")
    plt.close()  # Ferme la fenêtre de matplotlib proprement


# Fonction principale pour calculer l'image RGB
def calcule_true_rgb_opti(wl, reflectance_image):
    if wl < wlMin or wl > wlMax:
        print("La longueur d'onde est hors de la plage.")
        return None

    # Calcul de l'indice de la bande en fonction de la longueur d'onde
    k = round((wl - wlMin) / 2)
    reflectance = reflectance_image.read_band(k)  # Lecture des données de réflexion pour cette bande

    # Conversion de l'image de réflexion en un tableau NumPy
    reflectance = np.array(reflectance, dtype=np.float32)

    # Calcul des valeurs RGB pour chaque pixel
    r, g, b = nmToRGB(wl)
    true_rgb_img = np.zeros((reflectance.shape[0], reflectance.shape[1], 3), dtype=np.uint8)

    # Calcul des composantes RGB
    true_rgb_img[..., 0] = np.clip(r * reflectance * 255, 0, 255).astype(np.uint8)  # Rouge
    true_rgb_img[..., 1] = np.clip(g * reflectance * 255, 0, 255).astype(np.uint8)  # Vert
    true_rgb_img[..., 2] = np.clip(b * reflectance * 255, 0, 255).astype(np.uint8)  # Bleu

    max_value = np.max(true_rgb_img)

    # Vérification si la composante maximale peut être multipliée par 2 sans dépasser 255
    if max_value * 2 <= 255:
        true_rgb_img *= 2
    else:
        true_rgb_img = np.clip(true_rgb_img, 0, 255)  # Si saturation, on limite à 255

    return true_rgb_img

def calcule_rgb_3slid(wl_r, wl_g, wl_b, reflectance_image):
    wlMin, wlMax = 402, 998  # Plage de longueurs d'onde
    if reflectance_image is None:
        print("Erreur : image non chargée correctement.")
  
    reflectance_image = reflectance_image[:,:,(round((wl_r - wlMin) / 2),round((wl_g - wlMin) / 2),round((wl_b - wlMin) / 2))]

    return reflectance_image

def calcule_true_gray_opti(wl, reflectance_image):
    if wl < wlMin or wl > wlMax:
        print("La longueur d'onde est hors de la plage.")
        return None

    # Calcul de l'indice de la bande en fonction de la longueur d'onde
    k = round((wl - wlMin) / 2)
    reflectance = reflectance_image.read_band(k)  # Lecture des données de réflexion pour cette bande

    # Conversion de l'image de réflexion en un tableau NumPy
    reflectance = np.array(reflectance, dtype=np.float32)

    # Normalisation de la reflectance pour qu'elle soit comprise entre 0 et 1
    reflectance = np.clip(reflectance, 0, 1)

    # Mise à l'échelle des valeurs pour les convertir en niveaux de gris (0 à 255)
    gray_img = (reflectance * 255).astype(np.uint8)
    return gray_img


def calcule_rgb_plage2(wl_min, wl_max):
    """Reconstitue l'image RGB à partir d'une plage de longueurs d'onde."""
    img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale

    # Obtenir les dimensions de l'image
    nblines, nbcolones, nb_bandes = img.shape

    # Initialiser l'image RGB avec des zéros
    true_rgb_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)

    # Calcul des indices des longueurs d'onde
    for wl in range(wl_min, wl_max + 1, 2):  # On prend un pas de 2 pour suivre l'échantillonnage
        k = round((wl - 400) / 2)  # Calcul de l'indice correspondant à la bande
        if 0 <= k < nb_bandes:
            reflectance = img.read_band(k)  # Lecture de la bande k
            r, g, b = nmToRGB(wl)  # Conversion de la longueur d'onde en RGB
            true_rgb_img[:, :, 0] += r * reflectance
            true_rgb_img[:, :, 1] += g * reflectance
            true_rgb_img[:, :, 2] += b * reflectance
    # print(true_rgb_img.min())
    # print(true_rgb_img.max())

    true_rgb_img -= true_rgb_img.min()  # Ramène le minimum à 0
    true_rgb_img /= true_rgb_img.max()  # Normalisation entre 0 et 1
    true_rgb_img *= 255

    return true_rgb_img.astype(np.uint8)  # Convertir en entiers 8 bits pour l'affichage


def calcule_rgb_plage(img, metadata, wl_min_idx, wl_max_idx):
    """Reconstitue l'image RGB à partir d'une plage de longueurs d'onde définie par les indices."""
    
    nblines, nbcolones, nb_bandes = img.shape
    wavelengths = np.array(metadata['wavelength'], dtype=float)
    
    # Vérifier que les indices sont valides
    if not (0 <= wl_min_idx < len(wavelengths) and 0 <= wl_max_idx < len(wavelengths)):
        print("Indices de longueur d'onde hors limites.")
        return None
    
    # Sélectionner les longueurs d'onde et les indices correspondants
    selected_wls = wavelengths[wl_min_idx:wl_max_idx + 1]
    selected_indices = list(range(wl_min_idx, wl_max_idx + 1))
    
    if not selected_indices:
        print("Aucune longueur d'onde valide dans la plage donnée.")
        return None
    
    # Initialiser les matrices RGB
    true_rgb_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)
    
    # Charger toutes les bandes en une seule fois pour accélérer la lecture
    all_bands = np.array([img.read_band(k) for k in selected_indices])
    
    # Calcul des poids RGB
    rgb_weights = np.array([nmToRGB(wl) for wl in selected_wls])
    
    # Appliquer les poids RGB via un produit matriciel
    true_rgb_img[:, :, 0] = np.tensordot(all_bands, rgb_weights[:, 0], axes=(0, 0))
    true_rgb_img[:, :, 1] = np.tensordot(all_bands, rgb_weights[:, 1], axes=(0, 0))
    true_rgb_img[:, :, 2] = np.tensordot(all_bands, rgb_weights[:, 2], axes=(0, 0))
    
    # Normalisation
    true_rgb_img -= true_rgb_img.min()
    
    if true_rgb_img.max() > 0:
        true_rgb_img /= true_rgb_img.max()
        true_rgb_img *= 255

    else : 
        true_rgb_img.fill(0)

    true_rgb_img = np.nan_to_num(true_rgb_img, nan=0.0, posinf=255, neginf=0.0)

    
    return true_rgb_img.astype(np.uint8)

class CustomQRangeSlider(QRangeSlider):
    """Custom QRangeSlider that emits a signal when the slider is released."""
   
    sliderReleased = Signal(tuple)  # Define a custom signal that sends the slider values

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        """Initialize with the specified orientation (default: Horizontal)."""
        super().__init__(orientation, parent)  # Pass orientation to the parent class

    def mouseReleaseEvent(self, event):
        """Detects when the user releases the slider and emits the custom signal."""
        super().mouseReleaseEvent(event)  # Call the default behavior
        self.sliderReleased.emit(self.value())  # Emit signal with the current values



class CustomWidgetRangeSlider(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.wavelenghts = [i for i in range(10)]
        layout = QHBoxLayout(self)
       

        self.wl_min_label = QLabel()
        layout.addWidget(self.wl_min_label)
        self.range_slider = CustomQRangeSlider()
        layout.addWidget(self.range_slider)
        self.wl_max_label = QLabel()
        layout.addWidget(self.wl_max_label)

        self.setRange(self.wavelenghts)
        self.update_label((0,len(self.wavelenghts)-1))
        self.range_slider.setValue((0,len(self.wavelenghts)-1))


        self.range_slider.valueChanged.connect(self.update_label)

    def update_label(self, value):
        """Update labels and restrict slider movement to allowed values."""
       
        min_index, max_index = value  # Get slider positions
        min_value, max_value = self.wavelenghts[min_index], self.wavelenghts[max_index]  # Map indices to values
        self.wl_min_label.setText("{}".format(min_value))
        self.wl_max_label.setText("{}".format(max_value))
        """Reduit l'étude des clustering aux valeurs indiqués"""

    def setRange(self, wavelenghts):
        if wavelenghts:
            self.range_slider.setRange(0,len(wavelenghts)-1)
        else :
            print("WARNING : wavelenght is None in CustomWidgetRangeSlider.setRange(",wavelenghts ,")")
            self.range_slider.setRange(0,10)

    def setWavelenghts(self,wavelenghts):
        self.wavelenghts = wavelenghts
        self.setRange(self.wavelenghts) #update the range
        self.range_slider.setValue((0,len(wavelenghts)-1))


def main():
    img = calcule_true_rgb_opti(550)
    return 0


