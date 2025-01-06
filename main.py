import spectral as sp


sp.settings.envi_support_nonlowercase_params = True

wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)
print("hello world")

def main():
    img = sp.open_image("feuille_250624_ref.hdr")
    print(img)
    
    data = img.load()
    print(data)
    view = sp.imshow(img,(R,G,B))
    input("Press Enter to close the program...")

    print(view)
    return 0


print(main())

