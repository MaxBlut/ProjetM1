import spectral as sp
from PIL import Image
import numpy as np

# Set the envi_support_nonlowercase_params to True to avoid an error message 
sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
wlMax = 998


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
    


def calcule_true_rgb(wl=402):
    if wl > wlMin and wl < wlMax:
        k = round((wl-wlMin)/2)           # The indice of the wavelenght of the color
        rgb = sp.open_image("feuille_250624_ref.hdr").read_band(k)

        nblines = len(rgb)
        nbcolones = len(rgb[0])
        true_rgb_img = [[[0 for _ in range(3)] for _ in range(nbcolones)] for _ in range(nblines)]
        for i in range(0, nblines):
            for j in range(0, nbcolones):
                r, g, b = nmToRGB(wl)
                true_rgb_img[i][j][0] += r*rgb[i][j]*255
                true_rgb_img[i][j][1] += g*rgb[i][j]*255
                true_rgb_img[i][j][2] += b*rgb[i][j]*255
        print("True RGB image calculated")
        return true_rgb_img
    else:
        print("The wavelength is out of the range")
        return 1




def main():
    #img = sp.open_image("feuille_250624_ref.hdr")

    img = calcule_true_rgb(470)

    # Conversion de la liste en un tableau NumPy
    array = np.array(img, dtype=np.uint8)

    # Création de l'image à partir du tableau
    image = Image.fromarray(array, mode='RGB')

    # Sauvegarde de l'image
    image.save("output_image.png")

    # Affichage de l'image
    image.show()
    input("Press Enter to close the program...")

  

    """
    #view = sp.imshow(img,(R,G,B))
    input("Press Enter to close the program...")
    """
    return 0


print(main())

