import numpy as np


def are_intersecting(v1x2, v1y2, v2x1, v2y1, v2x2, v2y2, v1x1=-1, v1y1=-1):
    NO = 0
    YES = 1
    COLLINEAR = 2
    #j'ai copié ce code sur : https://stackoverflow.com/questions/217578/how-can-i-determine-whether-a-2d-point-is-within-a-polygon
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
    data = data[cluster_map == selected_cluster_value,:]
    nband = data.shape[1]  # Nombre de bandes spectrales
    moyenne = np.zeros(nband)  # Initialise la moyenne avec des zéros
    for j in range(nband):
        moyenne[j] = np.mean(data[:, j])  # Moyenne pour chaque bande spectral
    return moyenne