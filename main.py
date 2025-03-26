import spectral as sp
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from qtpy.QtCore import Qt

from superqt import QRangeSlider
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
# Set the envi_support_nonlowercase_params to True to avoid an error message 
sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
wlMax = 998
#reflectance_image = sp.open_image("feuille_250624_ref.hdr")
class RangeSliderInitializer:
    def __init__(self):
        self.qlrs = QRangeSlider(Qt.Horizontal)
        self.qlrs.setRange(402, 998)
        self.qlrs.setValue((402, 998))
        

    def get_slider(self):
        return self.qlrs

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
    # Calcul des bandes respectives

    # r_reflectance = reflectance_image.read_band(round((wl_r - wlMin) / 2))
    # g_reflectance = reflectance_image.read_band(round((wl_g - wlMin) / 2))
    # b_reflectance = reflectance_image.read_band(round((wl_b - wlMin) / 2))

    reflectance_image = reflectance_image[:,:,(round((wl_r - wlMin) / 2),round((wl_g - wlMin) / 2),round((wl_b - wlMin) / 2))]
    # Conversion en tableau NumPy
    # r_reflectance = np.array(r_reflectance, dtype=np.float32)
    # g_reflectance = np.array(g_reflectance, dtype=np.float32)
    # b_reflectance = np.array(b_reflectance, dtype=np.float32)

    # # Calcul des valeurs RGB pour chaque longueur d'onde
    # r, g, b = nmToRGB(wl_r)
    # true_rgb_img = np.zeros((r_reflectance.shape[0], r_reflectance.shape[1], 3), dtype=np.uint8)

    # # Appliquer les réflexions aux canaux respectifs
    # true_rgb_img[..., 0] = np.clip(r * r_reflectance * 255, 0, 255).astype(np.uint8)  # Rouge
    # true_rgb_img[..., 1] = np.clip(g * g_reflectance * 255, 0, 255).astype(np.uint8)  # Vert
    # true_rgb_img[..., 2] = np.clip(b * b_reflectance * 255, 0, 255).astype(np.uint8)  # Bleu

    # Affichage de l'image
    # plt.imshow(true_rgb_img)
    # plt.title(f"Image RGB - R: {wl_r}nm, G: {wl_g}nm, B: {wl_b}nm")
    # plt.axis('off')  # Ne pas afficher les axes
    # plt.show()
    # return true_rgb_img
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

    # Calcul du maximum des pixels pour vérifier si la saturation est possible
    # max_value = np.max(gray_img)

    # Vérification si la composante maximale peut être multipliée par 2 sans dépasser 255
    # if max_value * 2 <= 255:
    #     gray_img *= 2
    # else:
    #     gray_img = np.clip(gray_img, 0, 255)  # Si saturation, on limite à 255

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

def calcule_rgb_plage(img, wl_min, wl_max):
    """Reconstitue l'image RGB à partir d'une plage de longueurs d'onde de manière optimisée."""
    
    nblines, nbcolones, nb_bandes = img.shape

    # Calculer les indices des longueurs d'onde
    indices = [(wl, round((wl - 400) / 2)) for wl in range(wl_min, wl_max + 1, 2)]
    indices = [(wl, k) for wl, k in indices if 0 <= k < nb_bandes]

    if not indices:
        print("Aucune longueur d'onde valide dans la plage donnée.")
        return None

    # Initialiser les matrices RGB
    true_rgb_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)

    # Charger toutes les bandes en une seule fois pour accélérer la lecture
    all_bands = np.array([img.read_band(k) for _, k in indices])

    # Calcul des poids RGB
    rgb_weights = np.array([nmToRGB(wl) for wl, _ in indices])

    # Appliquer les poids RGB via un produit matriciel
    true_rgb_img[:, :, 0] = np.tensordot(all_bands, rgb_weights[:, 0], axes=(0, 0))
    true_rgb_img[:, :, 1] = np.tensordot(all_bands, rgb_weights[:, 1], axes=(0, 0))
    true_rgb_img[:, :, 2] = np.tensordot(all_bands, rgb_weights[:, 2], axes=(0, 0))

    # Normalisation
    true_rgb_img -= true_rgb_img.min()
    true_rgb_img /= true_rgb_img.max()
    true_rgb_img *= 255

    return true_rgb_img.astype(np.uint8)

def main():
    img = calcule_true_rgb_opti(550)
    #img2 = calcule_rgb_plage(400, 700)
    # # Conversion de la liste en un tableau NumPy
    # array = np.array(img, dtype=np.uint8)

    # # Utilisation de Matplotlib pour afficher l'image
    # fig, ax = plt.subplots()
    # ax.imshow(array)
    # ax.axis('off')  # Masquer les axes

    # # Connexion de la gestion de l'événement de fermeture
    # fig.canvas.mpl_connect('close_event',on_close )

    # # Affichage de la fenêtre et attente de la fermeture
    # plt.show()

    # # Sauvegarde de l'image
    # image = Image.fromarray(array, mode='RGB')
    # image.save("output_image.png")

    return 0

#print(main())

