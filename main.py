import spectral as sp
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Set the envi_support_nonlowercase_params to True to avoid an error message 
sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
wlMax = 998
reflectance_image = sp.open_image("feuille_250624_ref.hdr")


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
def calcule_true_rgb_opti(wl):
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



def calcule_true_gray_opti(wl):
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



def main():
    img = calcule_true_rgb_opti(550)

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

print(main())

