import sys
from PySide6.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random
import main
import spectral as sp




wlMin = 402
R = round((700-wlMin)/2) 
G = round((546.1-wlMin)/2)
B = round((435.8-wlMin)/2)

img = sp.open_image("feuille_250624_ref.hdr")
data = img.load()




class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure, self.ax = plt.subplots()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button1 = QPushButton('Plot')
        self.button1.clicked.connect(main.main)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button1)
        self.setLayout(layout)

    def main(self):
        input_var = ""
       
        while input_var !="y":
            RGB_img = data[:,:,(R,G,B)]
            self.ax.imshow(RGB_img)
            self.canvas.draw()
            coords = plt.ginput(50)
            if(len(coords) < 3):
                print("Il faut au moin 3 points !")
                input_var = ""
            else:
                X = [value[0] for value in coords]
                Y = [value[1] for value in coords] 
                main.plot_poly(X,Y)
                input_var = input("Etes vous satisfait de l'image ? (y/n) :\n")
            plt.close()
        map = main.check_inside_poly(X,Y)
        
    

    
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())