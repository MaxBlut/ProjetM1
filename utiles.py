import numpy as np
import spectral as sp
import numpy as np



# Set the envi_support_nonlowercase_params to True to avoid an error message 
sp.settings.envi_support_nonlowercase_params = True


from numpy import sqrt, log10

import re










def are_intersecting(v1x2, v1y2, v2x1, v2y1, v2x2, v2y2, v1x1=-1, v1y1=-1):
    # code inspiré par : https://stackoverflow.com/questions/217578/how-can-i-determine-whether-a-2d-point-is-within-a-polygon
    NO = 0
    YES = 1
    COLLINEAR = 2
    
    # Convert vector 1 to a line (line 1) of infinite length.
    a1 = v1y2 - v1y1
    b1 = v1x1 - v1x2
    c1 = (v1x2 * v1y1) - (v1x1 * v1y2)

    # Insert (x1,y1) and (x2,y2) of vector 2 into the equation above.
    d1 = (a1 * v2x1) + (b1 * v2y1) + c1
    d2 = (a1 * v2x2) + (b1 * v2y2) + c1

    # If d1 and d2 both have the same sign, they are both on the same side
    if (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0):
        return NO

    # Calculate the infinite line 2 in linear equation standard form.
    a2 = v2y2 - v2y1
    b2 = v2x1 - v2x2
    c2 = (v2x2 * v2y1) - (v2x1 * v2y2)

    # Calculate d1 and d2 again, this time using points of vector 1.
    d1 = (a2 * v1x1) + (b2 * v1y1) + c2
    d2 = (a2 * v1x2) + (b2 * v1y2) + c2

    # Again, if both have the same sign (and neither one is 0),
    if (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0):
        return NO

    # If they are collinear, they intersect in any number of points from zero to infinite.
    if (a1 * b2) - (a2 * b1) == 0.0:
        return COLLINEAR

    # If they are not collinear, they must intersect in exactly one point.
    return YES







def mean_spectre_of_cluster(cluster_map, data, selected_cluster_value=1):
    # Get the mean spectrum of a cluster in a hyperspectral image.
    # Args:
    #     cluster_map: 2D array of cluster labels.
    #     data: 3D array of hyperspectral data.
    #     selected_cluster_value: Value of the cluster to analyze.
    mask = cluster_map == selected_cluster_value
    avg_spectrum = np.mean(data[mask, :], axis=0)
    return avg_spectrum






# Extend the Axes class with `set_legend` and `get_legend`
def set_legend(ax, legend):
    """Manually sets a custom legend reference on the axis."""
    ax._custom_legend = legend





def get_legend(ax):
    """Returns the stored custom legend if it exists, otherwise None."""
    return getattr(ax, "_custom_legend", None)








def custom_clear(ax):
    ax.clear()
    set_legend(ax, None)









def closest_id(wl, wl_list, accuracy=5):
    id = None
    diff = accuracy
    for i in range(len(wl_list)):
        if wl_list[i] <= wl + accuracy:
            if abs(wl - wl_list[i]) < diff:
                diff = abs(wl - wl_list[i])
                id = i
        else:
            break
    return id












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
    









def calcule_true_rgb_opti(k, reflectance_image, wavelength):
    """ Fonction principale pour calculer l'image RGB """
    # Calcul de l'indice de la bande en fonction de la longueur d'onde
    
    reflectance = reflectance_image.read_band(k)  # Lecture des données de réflexion pour cette bande

    # Conversion de l'image de réflexion en un tableau NumPy
    reflectance = np.array(reflectance, dtype=np.float32)

    # Calcul des valeurs RGB pour chaque pixel
    r, g, b = nmToRGB(float(wavelength[k]))  # Conversion de la longueur d'onde en RGB
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













def calcule_true_gray_opti(k, reflectance_image):
    reflectance = reflectance_image.read_band(k)  # Lecture des données de réflexion pour cette bande

    # Conversion de l'image de réflexion en un tableau NumPy
    reflectance = np.array(reflectance, dtype=np.float32)

    # Normalisation de la reflectance pour qu'elle soit comprise entre 0 et 1
    reflectance = np.clip(reflectance, 0, 1)

    # Mise à l'échelle des valeurs pour les convertir en niveaux de gris (0 à 255)
    gray_img = (reflectance * 255).astype(np.uint8)
    return gray_img













def calcule_rgb_plage(img, wavelength, wl_min_idx, wl_max_idx):
    """Reconstitue l'image RGB à partir d'une plage de longueurs d'onde définie par les indices."""
    
    nblines, nbcolones, nb_bandes = img.shape
    wavelengths = np.array(wavelength, dtype=float)
    
    # Vérifier que les indices sont valides
    if not (0 <= wl_min_idx < len(wavelengths) and 0 <= wl_max_idx < len(wavelengths)):
        print("Indices de longueur d'onde hors limites.")
        return None
    
    # Sélectionner les longueurs d'onde et les indices correspondants
    selected_wls = wavelengths[wl_min_idx:wl_max_idx + 1]
    selected_indices = list(range(wl_min_idx, wl_max_idx + 1))
    
    if not selected_indices:
        print("Aucune longueur d'onde valide dans la plage donnée.")
        return None
    
    # Initialiser les matrices RGB
    true_rgb_img = np.zeros((nblines, nbcolones, 3), dtype=np.float32)
    
    # Charger toutes les bandes en une seule fois pour accélérer la lecture
    all_bands = np.array([img.read_band(k) for k in selected_indices])
    
    # Calcul des poids RGB
    rgb_weights = np.array([nmToRGB(wl) for wl in selected_wls])
    
    # Appliquer les poids RGB via un produit matriciel
    true_rgb_img[:, :, 0] = np.tensordot(all_bands, rgb_weights[:, 0], axes=(0, 0))
    true_rgb_img[:, :, 1] = np.tensordot(all_bands, rgb_weights[:, 1], axes=(0, 0))
    true_rgb_img[:, :, 2] = np.tensordot(all_bands, rgb_weights[:, 2], axes=(0, 0))
    
    # Normalisation
    true_rgb_img -= true_rgb_img.min()
    
    if true_rgb_img.max() > 0:
        true_rgb_img /= true_rgb_img.max()
        true_rgb_img *= 255

    else : 
        true_rgb_img.fill(0)

    true_rgb_img = np.nan_to_num(true_rgb_img, nan=0.0, posinf=255, neginf=0.0)

    
    return true_rgb_img.astype(np.uint8)

















def resolv_equation(equation,data_img,wavelengths):
    # Create a dictionary that maps RXXXX to the correct band in hyperspectral data
    local_dict = {}

    if "where" in equation:
        eq_list = equation.split("where", 1)

        for i in range(1, len(eq_list)): # we start at 1 to not include the first equation
            sub_eq = eq_list[i]
            if "=" in sub_eq:
                # Split the equation into variable and equation parts
                alpha, sub_eq = sub_eq.split("=", 1)
                alpha = alpha.strip()
                sub_eq = sub_eq.strip().rstrip(",")
                result = resolv_equation(sub_eq,data_img,wavelengths)
                local_dict[alpha] = result
        equation = eq_list[0].strip()
        
    # Extract wavelength values from the equation
    found_wavelengths = re.findall(r'R(\d+)', equation)
    
    if len(found_wavelengths)==0:
        print("no wl found in the equation text")
        return -2
    
    for wl in found_wavelengths:
        wl = int(wl)
        band_index = closest_id(wl,wavelengths,accuracy=2)
        if band_index is None:
            print("wl value not found")
            return -1
        data = data_img[:,:,band_index]
        local_dict[f'R{int(wl)}'] = np.squeeze(data)
    # Evaluate the equation safely
    local_dict['sqrt'] = sqrt
    local_dict['abs'] = abs
    local_dict['log'] = log10
    try:
        result = eval(equation, {"__builtins__": {}} , local_dict) 
    except Exception as e:
        raise ValueError(f"Error evaluating equation: {e}")
    return result