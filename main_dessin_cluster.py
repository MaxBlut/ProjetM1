import sys
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,QLabel, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import print_RGB.utiles as utiles

import spectral as sp
sp.settings.envi_support_nonlowercase_params = True




def plot_poly(X, Y):
    n =  len(X)
    for i in range(n):
        plt.plot([X[i],X[(i+1)%n]], [Y[i],Y[(i+1)%n]], 'ro-')
    return 0
    


class MatplotlibImage(QWidget):
    def __init__(self, RGB_img, data):
        super().__init__()
        self.figure, (self.Img_ax, self.second_ax) = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={'width_ratios': [2, 1]})
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)
        self.canvas = FigureCanvas(self.figure)
        self.second_ax.plot([])  # Initialize the second plot
        self.button_confirm = QPushButton('Confirm')
        self.button_confirm.clicked.connect(self.confirm_to_connect)
        self.button_delete = QPushButton('delete')
        self.button_delete.clicked.connect(lambda: self.delete("all"))
        
        self.label = QLabel("Click to add points, right-click to remove the last point, press enter to confirm the polygon, and delete to remove everything.")
        self.label.setContentsMargins(10,10,10,10)  # Set margin for the label
        self.label.setAlignment(Qt.AlignCenter)  # Center the text
        self.label.setSizePolicy(QSizePolicy.Preferred , QSizePolicy.Fixed)
        
        

        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setContentsMargins(10,10,10,10)
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.label)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_confirm)
        layout.addWidget(self.button_delete)
        self.setLayout(layout)
        
        self.Img_ax.imshow(RGB_img, cmap='gray')
        self.Img_ax.axis('off')

        self.data = data
        self.map = []           # Variable to store the map
        self.overlay = None     # Variable to store the overlay object for easy removal
        self.points = []        # List to store clicked points
        self.point_plots = []   # Store plotted points Object for easy removal
        self.line_polts = []    # Store plotted lines Object for easy removal
        
        # Connect mouse click event
        self.canvas.mpl_connect("button_press_event", self.on_click)
        
        # Bind the "Enter" key to the confirm button
        self.button_confirm.setShortcut("Return")
        self.button_delete.setShortcut("Delete")

        self.canvas.draw()


    def on_click(self, event):
        # Handle mouse click events.
        if event.xdata is not None and event.ydata is not None:
            if self.line_polts != []:
                self.delete("lines")
                self.button_confirm.clicked.disconnect()
                self.button_confirm.clicked.connect(self.confirm_to_connect)
            if event.button == 1:  # Left click to add a point
                point, = self.Img_ax.plot(event.xdata, event.ydata, 'rx')  # Mark click
                self.points.append((event.xdata, event.ydata))
                self.point_plots.append(point)
                # print(f"Added: {self.points[-1]}")
            elif event.button == 3 and self.points:  # Right click to remove the last point
                if self.overlay == None:
                    removed_point = self.points.pop()
                    point_to_remove = self.point_plots.pop()
                    point_to_remove.remove()  # Remove the last plotted point
                    # print(f"Removed: {removed_point}")
            
            self.canvas.draw()  # Update the figure


    def confirm_to_connect(self):
        # Connect the points with lines
        if self.points == []:
            return
        print("Connecting")
        # Disconnect all previous connections before reconnecting
        n =  len(self.points)
        for i in range(n):
            line, = self.Img_ax.plot([self.points[i][0],self.points[(i+1)%n][0]], [self.points[i][1],self.points[(i+1)%n][1]], 'r')
            self.line_polts.append(line)
        self.canvas.draw()
        self.button_confirm.clicked.disconnect()
        self.button_confirm.clicked.connect(self.confirm_to_fill)
        self.label.setText("Click to add points, right-click to remove the last point, press enter to confirm the polygon, and delete to remove everything. \n Press confirm to fill the polygon with color.")
        

    def confirm_to_fill(self):
        # Fill the polygon with color using a ray casting algorithm 
        print("Filling")
        # Disconnect all previous connections before reconnecting
        n = len(self.points)
        X = [self.points[i][0] for i in range(n)]
        Y = [self.points[i][1] for i in range(n)]
        shape = self.data.shape
        map = np.full((shape[0], shape[1]), False, dtype=bool)
        for i in range(int(min(X)), int(max(X))):
            for j in range(int(min(Y)), int(max(Y))):
                parite = 0
                for k in range(n):
                    parite += utiles.are_intersecting(i,j,X[k],Y[k],X[(k+1)%n],Y[(k+1)%n])
                if(parite % 2 == 1) and (parite != 0):
                    map[j,i] = True
        masked_overlay = np.ma.masked_where(~map, map)
        self.delete("all") 
        self.overlay = self.Img_ax.imshow(masked_overlay, cmap = "Reds_r", alpha = 0.6)
        self.map = map 
        self.canvas.draw()
        self.button_confirm.clicked.disconnect()
        self.button_confirm.clicked.connect(self.confirm_to_plot)
        self.label.setText("press enter to plot the mean spectrum of the selected shape, and delete to remove everything.")
    

    def confirm_to_plot(self):
        # Plot the mean spectrum of the selected cluster 
        print("Plotting")
        self.second_ax.plot(utiles.mean_spectre_of_cluster(self.map, self.data,True), label = "spectre moyen")
        self.delete("overlay")
        self.canvas.draw()
        self.label.setText("Click to add points, right-click to remove the last point, press enter to confirm the polygon, and delete to remove everything.")

    def delete(self, what):
        # Delete the overlay and/or points and/or lines from the image shown
        print("Deleting")
        self.button_confirm.clicked.disconnect()
        self.button_confirm.clicked.connect(self.confirm_to_connect)
        
        if what == "all" or what == "overlay":
            if self.overlay is not None:
                self.overlay.remove()
                self.overlay = None
                print("   - overlay deleted")
        
        if what == "all" or what == "points":
            n = len(self.points)
            if n != 0:
                print("   - points deleted")
                for i in range(n):
                    self.point_plots[i].remove()
                self.point_plots = []
                self.points = []

        if what == "all" or what == "lines":
            n = len(self.line_polts)
            if n != 0:
                print("   - lines deleted")
                for i in range(n):
                    self.line_polts[i].remove()
                self.line_polts = []
        self.canvas.draw()


class MainWindow_draw_cluster(QMainWindow):
    def __init__(self):
        wlMin = 402
        R = round((700-wlMin)/2) 
        G = round((550-wlMin)/2)
        B = round((450-wlMin)/2)
        data = sp.open_image("feuille_250624_ref.hdr").load()
        RGB_img = data[:,:,(R,G,B)]
        if RGB_img.max()*2 < 1:
            RGB_img *= 2
        RGB_img.max()


        super().__init__()
        self.setWindowTitle("Matplotlib in PyQt - Click Detection")
        self.widget = MatplotlibImage(RGB_img, data)
        self.setCentralWidget(self.widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow_draw_cluster()
    window.show()
    sys.exit(app.exec())




