import numpy as np
import spectral as sp
import matplotlib.pyplot as plt
import intersecting

sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)

img = sp.open_image("feuille_250624_ref.hdr")
data = img.load()



def plot_poly(X, Y):
    print(X)
    print(Y)    
    n =  len(X)
    print(n)
    for i in range(n):
        plt.plot([X[i],X[(i+1)%n]], [Y[i],Y[(i+1)%n]], 'ro-')
    return 0





def check_inside_poly(X,Y):
    n = len(X)
    shape = img.shape
    map = np.full((shape[0], shape[1]), 0, dtype=bool)
    parite = 0
    print(min(X), max(X))
    print(min(Y), max(Y))
    for i in range(min(X), max(X)):
        for j in range(min(Y), max(Y)):
            parite = 0
            for k in range(n):
                parite += intersecting.are_intersecting(j,i,X[k],Y[k],X[(k+1)%n],Y[(k+1)%n]) == 1
                if(parite % 2 == 0) and (parite != 0):
                    map[i,j] = True
    view = sp.imshow(data = data , classes=map)
    view.class_alpha=0.2
    view.set_display_mode("classes")
    view.refresh()
    plt.ginput(1)
    plt.close()
    return 0





def main():
    input_var = ""
    while input_var !="y":
        view = sp.imshow(img, (R,G,B),title="tracez un polygone en indiquant les angles avec clique gauche, vous pouvez annuler avec clique droit et mettre fin avec le clic molette")
        coords = plt.ginput(50)
        if(len(coords) < 3):
            print("Il faut au moin 3 points !")
            input_var = ""
        else:
            X = [int(value[0]) for value in coords]
            Y = [int(value[1]) for value in coords] 
            print(data.shape)
            plot_poly(X,Y)
            input_var = input("Etes vous satisfait de l'image ? (y/n) :\n")
        plt.close()
    check_inside_poly(X,Y)
    return 0


print(main())
