import numpy as np
import spectral as sp
from sklearn.cluster import KMeans, AgglomerativeClustering
import matplotlib.pyplot as plt
from time import time 

import os
os.environ['OMP_NUM_THREADS'] = '1'

t1 = time()
sp.settings.envi_support_nonlowercase_params = True

LOKY_MAX_CPU_COUNT = 4


img_filename = "feuille_250624_ref.hdr"
cluster_map_filename = "feuille_250624_ref_background_map.npy"


data = sp.open_image(img_filename).load()
full_map = np.load(cluster_map_filename)
foreground_map  = (full_map == 1)
subset_data = data[foreground_map,:]
subset_data = subset_data.reshape(-1, subset_data.shape[1])

print(subset_data.shape)
subset_data = subset_data[::10,:]
print(subset_data.shape)


# clustering = AgglomerativeClustering(n_clusters = 3,compute_full_tree = True, linkage = "complete" ).fit(subset_data)
clustering  = KMeans(n_clusters=4, random_state=0, n_init="auto").fit(subset_data)
labels = clustering.labels_

print(labels)

n_ligne,n_colones= full_map.shape
classes = np.full((n_ligne, n_colones), 0, dtype=int) #we initialize the classes with 0 (black) for the background
k=0   #we use a variable k because the dimentions of the second cluster map are 1xN with N the number of pixels that has been considered to be appart of the leaf
for i in range(n_ligne):
    for j in range(n_colones):
        if full_map[i,j] == 1:           #if the pixel is part of the leaf
            if k < len(labels):
                classes[i,j] = labels[k]+1   #for each pixel of the leaf we color it with the color of the cluster it belongs to 
                k+=1 

view = sp.imshow(data = data , classes=classes)
view.class_alpha=0.2
view.set_display_mode("classes")
view.refresh()
print(time()-t1)
input("Press Enter to exit ...\n")
plt.close()
