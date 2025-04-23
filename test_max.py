import spectral as sp
from utiles import closest_id
sp.settings.WX_GL_DEPTH_SIZE = 16

img = sp.open_image("D:/MAXIME/cours/4eme_annee/Projet_M1/feuille_250624_ref/feuille_250624_ref.hdr")

if 'wavelength' in img.metadata:
    wavelength = img.metadata['wavelength']
elif "Wavelength" in img.metadata:
    wavelength = img.metadata['Wavelength']
wavelength = [float(i) for i in wavelength]


R = closest_id(700, wavelength)
G = closest_id(550, wavelength)       
B = closest_id(450, wavelength)







sp.view_cube(img, bands=[R, G, B])