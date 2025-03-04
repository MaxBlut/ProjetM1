import numpy as np
import spectral as sp
import matplotlib.pyplot as plt
import intersecting
from matplotlib.backend_bases import MouseButton

sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)

img = sp.open_image("feuille_250624_ref.hdr")
data = img.load()



def plot_poly(X, Y):
    n =  len(X)
    for i in range(n):
        plt.plot([X[i],X[(i+1)%n]], [Y[i],Y[(i+1)%n]], 'ro-')
    return 0





def check_inside_poly(X,Y):
    n = len(X)
    shape = img.shape
    map = np.full((shape[0], shape[1]), False, dtype=bool)
    for i in range(int(min(X)), int(max(X))):
        for j in range(int(min(Y)), int(max(Y))):
            parite = 0
            for k in range(n):
                parite += intersecting.are_intersecting(i,j,X[k],Y[k],X[(k+1)%n],Y[(k+1)%n])
            if(parite % 2 == 1) and (parite != 0):
                map[j,i] = True
    view = sp.imshow(img, (R, G, B),  classes=map)
    view.class_alpha=0.5
    view.set_display_mode("overlay")
    view.refresh()
    plt.ginput(1,mouse_add = MouseButton.MIDDLE)
    plt.close()
    return map





def main():
    input_var = ""
    while input_var !="y":
        view = sp.imshow(img, (R,G,B),title="tracez un polygone en indiquant les angles avec clique gauche, vous pouvez annuler avec clique droit et mettre fin avec le clic molette")
        coords = plt.ginput(50)
        if(len(coords) < 3):
            print("Il faut au moin 3 points !")
            input_var = ""
        else:
            X = [value[0] for value in coords]
            Y = [value[1] for value in coords] 
            plot_poly(X,Y)
            input_var = input("Etes vous satisfait de l'image ? (y/n) :\n")
        plt.close()
    map = check_inside_poly(X,Y)
    return 0


print(main())
