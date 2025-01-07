import spectral as sp
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


sp.settings.envi_support_nonlowercase_params = True


nblines =  608
nbcolones = 968
color = [[0,0,0],[255,255,255],[255,0,0],[0,255,0],[0,0,255]]

def main():
    img = sp.open_image("feuille_250624_ref.hdr")
    
    (m, c) = sp.kmeans(img, 2, 3)
   

    clustered_img = [[[255 for _ in range(3)] for _ in range(nbcolones)] for _ in range(nblines)]
    for i in range(nblines):
        for j in range(nbcolones ):
            clustered_img[i][j] = color[m[i][j]] #m[i][j] is the cluster number of the pixel (i,j)

    
    array = np.array(clustered_img, dtype=np.uint8)
    image = Image.fromarray(array, mode='RGB')
    image.save('clustered_img.png')
    image.show()
    input("Press Enter to close the program...")
    
    return 0


print(main())

