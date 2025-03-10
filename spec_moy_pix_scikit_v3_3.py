import spectral as sp
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.backend_bases import MouseButton
import os

os.environ['OMP_NUM_THREADS'] = '4' 


sp.settings.envi_support_nonlowercase_params = True
np.random.seed(42)
spectra = []  # Liste pour stocker les spectres sélectionnés




def first_kmean(data_img):
    # Chargement des données
    reshaped_data = data_img.reshape(-1, data_img.shape[-1])  # Aplatir en 2D

    # Clustering avec sklearn
    kmeans = KMeans(n_clusters=2, n_init='auto', max_iter=20, random_state=42)
    labels = kmeans.fit_predict(reshaped_data)

    # Reconstruction en 2D
    m = labels.reshape(data_img.shape[:-1])

    # Affichage pour choisir la classe de la feuille
    sp.imshow(classes=m, title="Sélectionnez la classe de la feuille")
    coords = plt.ginput(1)
    x, y = int(coords[0][0]), int(coords[0][1])
    plt.close()

    # Vérification et inversion des classes si besoin
    if m[y, x] == 0:
        m = 1 - m

    return m


def extract_one_cluster(data_img, first_cluster_map):
    #this function is used to extract one cluster from the image
    #it takes the image and the cluster map as input and return a new hdr file with only the pixels of the leaf
    selected_cluster_mask  = (first_cluster_map == 1)  # Masque des pixels de la même classe que le clic
    subset_data = data_img[selected_cluster_mask,:]
    subset_data.reshape(1, -1, subset_data.shape[1]), # Reshape en 1 ligne
    return subset_data


def second_kmean(n_clusters, iteration,first_cluster_map, data_first_cluster):
    # Chargement des données
    reshaped_data = data_first_cluster.reshape(-1, data_first_cluster.shape[-1])  # Aplatir en 2D
    # Clustering avec sklearn
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto', max_iter=iteration, random_state=42)
    labels = kmeans.fit_predict(reshaped_data)
    # Reconstruction de la carte des clusters
    second_clustered_data = labels.reshape((1, -1)) 

    # Création de l'image des classes avec fond noir et couleurs pour les clusters de la feuille
    mask = (first_cluster_map == 1)  # Masque des pixels de la feuille
    classes = np.zeros_like(first_cluster_map, dtype=int)  # Init classes avec le fond noir
    classes[mask] = second_clustered_data[0][:np.count_nonzero(mask)] + 1  # Applique la couleur
    return classes


def spectre_moyen_cluster(data_img, second_cluster_map):
    input_var = ""
    while input_var == "":
        plt.imshow(second_cluster_map,  cmap="nipy_spectral")
        plt.title("Please click on the leaf to select its cluster")
        coords = plt.ginput(1, mouse_add = MouseButton.RIGHT, mouse_pop = MouseButton.LEFT, timeout = 0)
        if coords != []:
            print(coords)
            x, y = int(coords[0][0]), int(coords[0][1])  # Coordonnées du clic
            plt.close()

            cluster_i = second_cluster_map[y, x]  # Classe du clic  

            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=second_cluster_map.min(), vmax=second_cluster_map.max())
            color_displayed = cmap(norm(cluster_i))[:3] 

            mask = (second_cluster_map == cluster_i)
            cluster_data = data_img[mask, :]
            if cluster_data.size == 0:
                print("Aucun pixel trouvé pour ce cluster.")
                continue
            print(cluster_data.shape)

            npixels = cluster_data.shape[0]  # Nombre de pixels du cluster
            nband = cluster_data.shape[1]  # Nombre de bandes spectrales
            print(cluster_data[0][0])
            moyenne = np.zeros(nband)  # Initialise la moyenne avec des zéros
            wavelength = [402 + 2 * i for i in range(nband)]  # Les longueurs d'onde

            for j in range(nband):
                print(j, "/", nband)
                moyenne[j] = np.mean(cluster_data[:, j])  # Moyenne pour chaque bande spectral

            # Ajouter le spectre à la liste pour superposer les spectres
            spectra.append((wavelength, moyenne, color_displayed))

            # Superposer tous les spectres précédemment cliqués
            plt.figure()
            for w, m, c in spectra:
                plt.plot(w, m, color=c)
            plt.title("Spectres superposés")
            plt.show()
    
            input_var = input("Press Enter to continue or any other key to stop...\n")

    plt.close()
    return 0



def spectre_moyen_de_tout_cluster(data_img, second_cluster_map):
    cmap_name = "nipy_spectral"
    AxesImage = plt.imshow(second_cluster_map,  cmap=cmap_name)
    n_cluster = len(set(second_cluster_map))
    cmap = plt.get_cmap(cmap_name)
    norm = plt.Normalize(vmin=second_cluster_map.min(), vmax=second_cluster_map.max())
    color_displayed = cmap(norm(cluster_i))[:3] 
    
    for i in range(n_cluster):
        mask = (second_cluster_map == i)
        cluster_data = data_img[mask, :]
        moyenne = np.zeros(nband)  # Initialise la moyenne avec des zéros
        wavelength = [402 + 2 * i for i in range(nband)]  # Les longueurs d'onde
        for j in range(nband):
            moyenne[j] = np.mean(cluster_data[:, j])  # Moyenne pour chaque bande spectral


    input_var = ""
    while input_var == "":
        
        plt.title("Please click on the leaf to select its cluster")
        coords = plt.ginput(1, mouse_add = MouseButton.RIGHT, mouse_pop = MouseButton.LEFT, timeout = 0)
        if coords != []:
            print(coords)
            x, y = int(coords[0][0]), int(coords[0][1])  # Coordonnées du clic
            plt.close()

            cluster_i = second_cluster_map[y, x]  # Classe du clic  

            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=second_cluster_map.min(), vmax=second_cluster_map.max())
            color_displayed = cmap(norm(cluster_i))[:3] 

            mask = (second_cluster_map == cluster_i)
            cluster_data = data_img[mask, :]
            if cluster_data.size == 0:
                print("Aucun pixel trouvé pour ce cluster.")
                continue
            print(cluster_data.shape)

            nband = cluster_data.shape[1]  # Nombre de bandes spectrales
            print(cluster_data[0][0])
            moyenne = np.zeros(nband)  # Initialise la moyenne avec des zéros
            wavelength = [402 + 2 * i for i in range(nband)]  # Les longueurs d'onde

            for j in range(nband):
                moyenne[j] = np.mean(cluster_data[:, j])  # Moyenne pour chaque bande spectral

            # Ajouter le spectre à la liste pour superposer les spectres
            spectra.append((wavelength, moyenne, color_displayed))

            # Superposer tous les spectres précédemment cliqués
            plt.figure()
            for w, m, c in spectra:
                plt.plot(w, m, color=c)
            plt.title("Spectres superposés")
            plt.show()
    
            input_var = input("Press Enter to continue or any other key to stop...\n")

    plt.close()
    return 0


def main(img_filename = "feuille_250624_ref.hdr"):

    # global data_img
    data_img = sp.open_image(img_filename).load()
    
    first_cluster_map = first_kmean(data_img)
    data_first_cluster = extract_one_cluster(data_img, first_cluster_map)
    second_cluster_map = second_kmean(6,25,first_cluster_map,data_first_cluster)
    spectre_moyen_cluster(data_img,second_cluster_map)
    


main()