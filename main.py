import spectral as sp
from spectral.io import envi
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


sp.settings.envi_support_nonlowercase_params = True


nblines =  608
nbcolones = 968
color = [[0,0,0],[255,255,255],[255,0,0],[0,255,0],[0,0,255]]

def main():
    # img = sp.open_image("feuille_250624_ref.hdr")
   
    # (m, c) = sp.kmeans(img, 2, 20)
    # np.save("cluster_map.npy", m)
    
    
    
    img = sp.open_image("feuille_250624_ref.hdr")
    
    m = np.load("cluster_map.npy")
    
    selected_cluster_mask  = (m == 1)
    
   
    subset_data = []
    for i in range(nblines):
        for j in range(nbcolones ):
            if selected_cluster_mask[i][j]:
                subset_data.append(img[i, j])
    
    # subset_data = np.array(subset_data)
    # subset_data_reshaped  = subset_data.reshape((-1, img.shape[-1]))
    print("subset reshaped")
    # m = sp.kmean(subset_data_reshaped, 3, 20)
    m = sp.kmeans(subset_data, 3, 20)
    np.save("clusted_cluster_map.npy", m)




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

