import spectral as sp


sp.settings.envi_support_nonlowercase_params = True


def main():
    img = sp.open_image("feuille_250624_ref.hdr")
    sp.imshow(sp.get_rgb(source = img))
    input("Press Enter to close the program...")
    return 0


print(main())

