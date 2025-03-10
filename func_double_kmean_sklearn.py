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

img_filename = None




def change_filename(filename, txt):
    newfilename = list(filename)            #we change the name of the file to save the cluster map
    for i in range(4):                      #we create the name of the new file from the input file name
        newfilename.pop()
    newfilename += txt
    newfilename = ''.join(newfilename)
    return newfilename


def first_kmean():
    # Chargement des données
    data = sp.open_image(img_filename).load()
    reshaped_data = data.reshape(-1, data.shape[-1])  # Aplatir en 2D

    # Clustering avec sklearn
    kmeans = KMeans(n_clusters=2, n_init='auto', max_iter=20, random_state=42)
    labels = kmeans.fit_predict(reshaped_data)

    # Reconstruction en 2D
    m = labels.reshape(data.shape[:-1])

    # Affichage pour choisir la classe de la feuille
    sp.imshow(classes=m, title="Sélectionnez la classe de la feuille")
    coords = plt.ginput(1)
    x, y = int(coords[0][0]), int(coords[0][1])
    plt.close()

    # Vérification et inversion des classes si besoin
    if m[y, x] == 0:
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

def second_kmean(n_clusters, iteration, cluster_filename="feuille_250624_ref_selected_cluster.hdr"):
    # Chargement des données
    data = sp.open_image(cluster_filename).load()
    reshaped_data = data.reshape(-1, data.shape[-1])  # Aplatir en 2D
    
    # Clustering avec sklearn
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto', max_iter=iteration, random_state=42)
    labels = kmeans.fit_predict(reshaped_data)

    # Reconstruction de la carte des clusters
    clustered_map = labels.reshape((1, -1))  # Garder cohérence avec `color_cluster()`
    np.save(change_filename(cluster_filename, "_reclustered.npy"), clustered_map)
    return 0


def color_cluster(second_cluster_map="feuille_250624_ref_selected_cluster_reclustered.npy",
                             fisrt_clusters_map="feuille_250624_ref_background_map.npy"):

    fisrt_clusters_map = np.load(fisrt_clusters_map)
    second_cluster_map = np.load(second_cluster_map)
    
    # Création de l'image des classes avec fond noir et couleurs pour les clusters de la feuille
    mask = (fisrt_clusters_map == 1)  # Masque des pixels de la feuille
    classes = np.zeros_like(fisrt_clusters_map, dtype=int)  # Init classes avec le fond noir
    classes[mask] = second_cluster_map[0][:np.count_nonzero(mask)] + 1  # Applique la couleur
    # Sauvegarde de l'image
    np.save(change_filename(img_filename, "_fully_mapped_cluster.npy"), classes)
    return 0



def spectre_moyen_cluster(fully_mapped_cluster="feuille_250624_ref_fully_mapped_cluster.npy"):
    input_var = ""
    fully_mapped_cluster = np.load(fully_mapped_cluster)
    img = sp.open_image(img_filename)

    while input_var == "":
        plt.imshow(fully_mapped_cluster,  cmap="nipy_spectral")
        plt.title("Please click on the leaf to select its cluster")
        coords = plt.ginput(1, mouse_add = MouseButton.RIGHT, mouse_pop = MouseButton.LEFT)
        if coords != []:
            print(coords)
            x, y = int(coords[0][0]), int(coords[0][1])  # Coordonnées du clic
            plt.close()

            cluster_i = fully_mapped_cluster[y, x]  # Classe du clic  

            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(vmin=fully_mapped_cluster.min(), vmax=fully_mapped_cluster.max())
            color_displayed = cmap(norm(cluster_i))[:3] 

            mask = (fully_mapped_cluster == cluster_i)
            cluster_data = img.load()[mask, :]
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




def main():
    global img_filename
    img_filename = "feuille_250624_ref.hdr"
    first_kmean()
    extract_one_cluster()
    second_kmean(6,25)
    color_cluster()
    spectre_moyen_cluster()
    


main()