import spectral as sp
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)

nblines = 608
nbcolones = 299

def main():
    img = sp.open_image("feuille_250624_ref.hdr")
    
    (m, c) = sp.kmeans(img, 2, 20)
    # plt.figure()
    # # for i in range(c.shape[0]):
    # #     plt.plot(c[i])
    # # plt.grid()
    # plt.plot(m)
    # print("c: ",c)
    # print("m: ",m)
    # plt.show()
    print("c",c)
    print("len(c) ",len(c))
    print("m",m)
    print("len(m) ",len(m))
    print("len(m[0]) ",len(m[0]))


    # clustered_img = [[[255 for _ in range(3)] for _ in range(nbcolones)] for _ in range(nblines)]
    # for i in range(nblines):
    #     for j in range(nbcolones):
    #         if m[i][j] != 0:
    #             clustered_img[i][j] = [0, 0, 0]


    # array = np.array(clustered_img, dtype=np.uint8)
    # image = Image.fromarray(array, mode='RGB')
    # image.save('clustered_img.png')
    # image.show()
    # input("Press Enter to close the program...")
    
    return 0


print(main())

