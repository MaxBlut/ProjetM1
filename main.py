import spectral as sp
import matplotlib.pyplot as plt

sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)





def plot_poly(coords):
    plt.plot((int(coords[0][0]),int(coords[0][1])), (int(coords[1][0]),int(coords[1][1])), 'ro-')
    # for i in range(4):
    #     plt.plot((int(coords[i][0]),int(coords[i][1])), (int(coords[(i+1)%4][0]),int(coords[(i+1)%4][1])), 'ro-')














def main():
    img = sp.open_image("feuille_250624_ref.hdr")
    data = img.load()
   
    view = sp.imshow(img, (R,G,B))
    input_var = ""
    coords = []
    while input_var !="y":
        coords = plt.ginput(4)
        if(len(coords) != 4):
            print("Il faut 4 points !")
            input_var = ""
        else:
            print(coords)
            plot_poly(coords)
            input_var = input("Etes vous satisfait de l'image ? (y/n) :\n")


   

    plt.close()
    return 0


print(main())

