import spectral as sp
import numpy as np
import matplotlib.pyplot as plt


sp.settings.envi_support_nonlowercase_params = True
np.random.seed(42)

img_filename = None






def change_filename(filename, txt):
    newfilename = list(filename)            #we change the name of the file to save the cluster map
    for i in range(4):                      #we create the name of the new file from the input file name
        newfilename.pop()
    newfilename += txt
    newfilename = ''.join(newfilename)
    return newfilename






def first_kmean():
    # the first kmean is used to cluster the image into 2 clusters (background and leaf)
    data = sp.open_image(img_filename).load()
    m, _ = sp.kmeans(data, 2, 20)


    sp.imshow(classes=m, title="Please click on the leaf to select it's cluster")
    coords = plt.ginput(1)                                                          # Attendre 1 clic
    x, y = int(coords[0][0]), int(coords[0][1])                                     # Coordonnées du clic
    plt.close()
    if m[y, x] == 0:                                                                # Si la classe de la feuille est zero, on inverse les classes
        m = 1 - m

    np.save(change_filename(img_filename, "_background_map.npy"), m)
    return 0 







def extract_one_cluster(cluster_map_filename = "feuille_250624_ref_background_map.npy"):
    #this function is used to extract one cluster from the image
    #it takes the image and the cluster map as input and return a new hdr file with only the pixels of the leaf
    img = sp.open_image(img_filename)
    data = img.load()
    m = np.load(cluster_map_filename)

    selected_cluster_mask  = (m == 1)  # Masque des pixels de la même classe que le clic
    subset_data = data[selected_cluster_mask,:]
    new_header = {
        'description': 'Subset of selected pixels',
        'samples': subset_data.shape[0],  # Nombre de pixels sélectionnés
        'lines': 1,                           # On n'a plus de structure 2D
        'bands': subset_data.shape[1],    # Nombre de bandes spectrales
        'header offset': 0,
        'file type': 'ENVI Standard',
        'data type': 4,                       # Type de données (par exemple, float32)
        'interleave': 'bsq',                  # Band sequential
        'byte order': 0,
        'wavelength': img.metadata.get('wavelength', []),
    }
    sp.envi.save_image(
        change_filename(img_filename, "_selected_cluster.hdr"),
        subset_data.reshape(1, -1, subset_data.shape[1]),  # Reshape en 1 ligne
        metadata=new_header,
        force=True
    )
    return 0







def second_kmean(n_clusters = 3, iteration = 20, cluster_filename = "feuille_250624_ref_selected_cluster.hdr"):
    #this function is used to cluster the leaf into n clusters to recognize the different parts of the leaf
    data = sp.open_image(cluster_filename).load()
    m, _ = sp.kmeans(data, n_clusters, iteration)
    np.save(change_filename(cluster_filename, "_reclustered.npy"), m)
    return 0







def color_cluster(second_cluster_map = "feuille_250624_ref_selected_cluster_reclustered.npy",fisrt_clusters_map = "feuille_250624_ref_background_map.npy"):
    
    #this function is used to color the different clusters of the leaf 
    #the background is colored in black and the different clusters of the leaf are colored in different colors
    fisrt_clusters_map = np.load(fisrt_clusters_map)
    second_cluster_map = np.load(second_cluster_map)
    classes = np.full((fisrt_clusters_map.shape[0], fisrt_clusters_map.shape[1]), 0, dtype=int) #we initialize the classes with 0 (black) for the background

    k=0   #we use a variable k because the dimentions of the second cluster map are 1xN with N the number of pixels that has been considered to be appart of the leaf
    for i in range(fisrt_clusters_map.shape[0]):
        for j in range(fisrt_clusters_map.shape[1]):
            if fisrt_clusters_map[i,j] == 1:                #if the pixel is part of the leaf
                classes[i,j] = second_cluster_map[0][k]+1   #for each pixel of the leaf we color it with the color of the cluster it belongs to 
                k+=1                                        #we add 1 to the color because indices of the second cluster map also start from 0 but they are not the background
    view = sp.imshow(data = sp.open_image(img_filename) , classes=classes)                       #we display the colored image
    # while(input("Press Enter to close the program...")):
    view.class_alpha=0.2
    view.set_display_mode("classes")
    view.refresh()
    input("Press Enter to close the program...")
    np.save(change_filename(img_filename, "_fully_mapped_cluster.npy"), classes)
    return 0







def spectre_moyen_cluster(fully_mapped_cluster="feuille_250624_ref_fully_mapped_cluster.npy"):
    input_var = ""
    fully_mapped_cluster = np.load(fully_mapped_cluster)
    img = sp.open_image(img_filename)
    while input_var == "":
        
        
        sp.imshow(classes=fully_mapped_cluster, title="Please click on the leaf to select it's cluster")
        coords = plt.ginput(1)                                                          # Attendre 1 clic
        x, y = int(coords[0][0]), int(coords[0][1])                                     # Coordonnées du clic
        plt.close()

        cluster_i = fully_mapped_cluster[y, x]                                          # Classe du clic        
        cluster_data = np.array(img.load()[(fully_mapped_cluster == cluster_i),:])                # Données du cluster
        print(cluster_data.shape)

        npixels = cluster_data.shape[0]                                        # Nombre de pixels du cluster
        nband = cluster_data.shape[1]                                          # Nombre de bandes spectrales
        print(cluster_data[0][0])
        moyenne = [0.0 for _ in range(nband)]
        wavelength = [402+2*i for i in range(nband)]
        for j in range(nband ):
            print(j,"/",nband)
            for i in range(npixels):
                moyenne[j] += cluster_data[i][j]
            moyenne[j] /= npixels
        couleur = input("Enter the color of the cluster: \n")
        plt.plot(wavelength,moyenne,color=couleur)
        
        input_var = input("Press Enter to continue or any other key to stop...\n")
    plt.show()
    plt.ginput(1) 
    plt.close()
    return 0 






def main():
    global img_filename
    img_filename = "feuille_250624_ref.hdr"
    # first_kmean()
    # extract_one_cluster()
    # second_kmean(15,25)
    # color_cluster()
    spectre_moyen_cluster()
    


print(main())



