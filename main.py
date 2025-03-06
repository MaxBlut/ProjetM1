import spectral as sp
from PIL import Image
import numpy as np
from spectral import open_image
import colour
import colour
from colour.models import XYZ_to_RGB
from colour.utilities import tsplit

# Charger les CMFs CIE 1931 pour les trois récepteurs (X, Y, Z)
def load_cie_cmfs():
    # CIE 1931 Standard Observer CMFs à 2nm d'intervalle de 380 nm à 780 nm
    cie_1931 = colour.models.SDS_10_DEG_1931
    wavelengths = np.arange(380, 781, 2)
    cmf = [cie_1931(wl) for wl in wavelengths]  # Correspondance couleur pour chaque longueur d'onde
    return np.array(cmf)

def nm_to_XYZ(wavelength, reflectance, cmfs):
    """Calculer la contribution XYZ d'une longueur d'onde spécifique."""
    # Intégration discrète sur la longueur d'onde pour obtenir XYZ
    xyz = np.zeros(3)
    for i in range(3):  # X, Y, Z
        xyz[i] = np.sum(reflectance * cmfs[:, i])  # Somme pondérée des CMFs et de la réflexion
    return xyz

def calcule_true_rgb_cie(wl_min, wl_max):
    """Reconstituer l'image RGB à partir d'une plage de longueurs d'onde en utilisant les CMFs CIE 1931."""
    img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale

    # Charger les CMFs CIE 1931 pour l'intégration
    cmfs = load_cie_cmfs()

    # Obtenir les dimensions de l'image
    nblines, nbcolones, nb_bandes = img.shape

    # Initialiser l'image XYZ et RGB
    true_xyz_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)

    # Calcul des indices des longueurs d'onde
    for wl in range(wl_min, wl_max + 1, 2):  # On prend un pas de 2 pour suivre l'échantillonnage
        k = round((wl - 402) / 2)  # Calcul de l'indice correspondant à la bande
        if 0 <= k < nb_bandes:
            reflectance = img.read_band(k)  # Lecture de la bande k
            xyz = nm_to_XYZ(wl, reflectance, cmfs)  # Calcul de la contribution XYZ
            true_xyz_img[:, :, 0] += xyz[0]  # X
            true_xyz_img[:, :, 1] += xyz[1]  # Y
            true_xyz_img[:, :, 2] += xyz[2]  # Z

    # Normalisation pour éviter d'avoir des valeurs supérieures à 255
    true_xyz_img -= true_xyz_img.min()
    true_xyz_img /= true_xyz_img.max()
    true_xyz_img *= 255

    # Conversion de XYZ à RGB
    true_rgb_img = XYZ_to_RGB(true_xyz_img)

    return np.clip(true_rgb_img, 0, 255).astype(np.uint8)


# Activer la prise en charge des paramètres non minuscules dans spectral
sp.settings.envi_support_nonlowercase_params = True

wlMin = 402  # Longueur d'onde minimale

wlMax = 998  # Longueur d'onde maximale


def nmToRGB(wavelength):
    """Convertit une longueur d'onde en valeurs RGB."""
    red, green, blue = 0.0, 0.0, 0.0
    if 380 <= wavelength < 440:
        red = -(wavelength - 440) / (440 - 380)
        blue = 1.0
    elif 440 <= wavelength < 490:
        green = (wavelength - 440) / (490 - 440)
        blue = 1.0
    elif 490 <= wavelength < 510:
        green = 1.0
        blue = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        red = (wavelength - 510) / (580 - 510)
        green = 1.0
    elif 580 <= wavelength < 645:
        red = 1.0
        green = -(wavelength - 645) / (645 - 580)
    elif 645 <= wavelength < 781:
        red = 1.0
    return red, green, blue


def calcule_true_rgb(wl_min, wl_max):
    """Reconstitue l'image RGB à partir d'une plage de longueurs d'onde."""
    img = sp.open_image("feuille_250624_ref.hdr")  # Charger l'image hyperspectrale

    # Obtenir les dimensions de l'image
    nblines, nbcolones, nb_bandes = img.shape

    # Initialiser l'image RGB avec des zéros
    true_rgb_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)

    # Calcul des indices des longueurs d'onde
    for wl in range(wl_min, wl_max + 1, 2):  # On prend un pas de 2 pour suivre l'échantillonnage
        k = round((wl - wlMin) / 2)  # Calcul de l'indice correspondant à la bande
        if 0 <= k < nb_bandes:
            reflectance = img.read_band(k)  # Lecture de la bande k
            r, g, b = nmToRGB(wl)  # Conversion de la longueur d'onde en RGB
            true_rgb_img[:, :, 0] += r * reflectance
            true_rgb_img[:, :, 1] += g * reflectance
            true_rgb_img[:, :, 2] += b * reflectance

    # Normalisation pour éviter d'avoir des valeurs supérieures à 255
    true_rgb_img -= true_rgb_img.min()
    true_rgb_img /= true_rgb_img.max()
    true_rgb_img *= 255

    print("Image RGB calculée à partir de la plage de longueurs d'onde")
    return true_rgb_img.astype(np.uint8)  # Convertir en entiers 8 bits pour l'affichage



def main():
    # Reconstituer l'image RGB en intégrant toutes les longueurs d'onde entre 450 et 650 nm
    # img = calcule_true_rgb(600, 700)

    # # Convertir le tableau en image PIL
    # image = Image.fromarray(img, mode='RGB')

    # # Sauvegarde et affichage
    # image.save("output_image.png")
    # image.show()
    # Sélectionner la plage de longueurs d'onde (450-650 nm par exemple)
    wl_min = 450
    wl_max = 650

    # Reconstituer l'image RGB avec une conversion CIE 1931
    img = calcule_true_rgb_cie(wl_min, wl_max)

    # Convertir le tableau en image PIL
    image = Image.fromarray(img, mode='RGB')

    # Sauvegarde et affichage
    image.save("output_image_cie.png")
    image.show()
    input("Press Enter to close the program...")

    return 0


print(main())
