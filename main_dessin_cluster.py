import sys
import spectral as sp
import numpy as np
import matplotlib.pyplot as plt

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QWidget, QVBoxLayout, QPushButton,QLabel, QSizePolicy, QHBoxLayout, QFileDialog
from PySide6.QtCore import Signal
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from utiles import mean_spectre_of_cluster, are_intersecting

from CustomElement import CustomCanvas,hyperspectral_appli

sp.settings.envi_support_nonlowercase_params = True




class MainWindow_draw_cluster(QWidget):
    def __init__(self, resize_signal):
        super().__init__()
        self.setWindowTitle("Matplotlib in PyQt - Click Detection")
        self.variable_init()
        self.init_ui()
        resize_signal.connect(self.on_resize)
        


    def variable_init(self):
        self.file_path = None   # chemin d'acces du fichier HDR
        self.overlay_number = 0
        self.data_img = None
        self.map = []           # Variable to store the map
        self.overlay = None     # Variable to store the overlay object for easy removal
        self.points = []        # List to store clicked points
        self.point_plots = []   # Store plotted points Object for easy removal
        self.line_plots = []    # Store plotted lines Object for easy removal
        self.croped_wavelength = None   # liste des longueurs d'ondes comprises entre les valeurs min et max du double slider
        self.wavelengths = None    # liste de toutes les longueurs d'ondes enregistré par la cam
        self.WL_MIN = None        # la valeur de la plus petite longueur d'onde enregistré par la caméra (constante)
        self.wl_min_cursor = None       # l'inice de longueur d'onde min du slider
        self.wl_max_cursor = None       # l'inice de longueur d'onde max du slider


    def init_ui(self):

        import_com_layout = QHBoxLayout()
        self.import_button = QPushButton("Importer un fichier")
        layout = QVBoxLayout()

        # Label d'information
        self.label = QLabel("Click to add points, right-click to remove the last point, press enter to confirm the polygon, and delete to remove everything.")
        self.label.setAlignment(Qt.AlignCenter)  # Center the text
        self.label.setSizePolicy(QSizePolicy.Preferred , QSizePolicy.Fixed)
        layout.addWidget(self.label)
        
       

        # matplotlib figure
        self.figure, self.axs = plt.subplots(1, 2, figsize=(15, 10), gridspec_kw={'width_ratios': [1, 1]})
        self.figure.subplots_adjust(top=0.96, bottom=0.08, left=0.03, right=0.975, hspace=0.18, wspace=0.08)

        # custom canvas for pickable legend on both axs
        self.canvas = CustomCanvas(self.figure, self.axs)

        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.canvas.draw()

        # buttons
        self.button_confirm = QPushButton('Confirm')
        self.button_confirm.clicked.connect(self.confirm_to_connect)
        layout.addWidget(self.button_confirm)
        self.button_delete = QPushButton('delete')
        self.button_delete.clicked.connect(lambda: self.delete("all"))
        layout.addWidget(self.button_delete)

        self.setLayout(layout)
        
        # Connect mouse click event
        self.canvas.mpl_connect("button_press_event", self.on_click)
        # Bind the "Enter" key to the confirm button
        self.button_confirm.setShortcut("Return")
        self.button_delete.setShortcut("Delete")
        
        
    def on_resize(self):
        print("rsize_event")
        



    def on_click(self, event):
        # Handle mouse click events.
        if hasattr(event, "handled") and event.handled:  # If the event was marked as handled, ignore it
            return
        
        if self.toolbar._actions['pan'].isChecked() or self.toolbar._actions['zoom'].isChecked():
            return
        if event.xdata is not None and event.ydata is not None:
            if self.line_plots != []:
                self.delete("lines")
                self.button_confirm.clicked.disconnect()
                self.button_confirm.clicked.connect(self.confirm_to_connect)
            if event.button == 1:  # Left click to add a point
                point, = self.axs[0].plot(event.xdata, event.ydata, 'rx')  # Mark click
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
            line, = self.axs[0].plot([self.points[i][0],self.points[(i+1)%n][0]], [self.points[i][1],self.points[(i+1)%n][1]], 'r')
            self.line_plots.append(line)
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
        shape = self.data_img.shape
        map = np.full((shape[0], shape[1]), False, dtype=bool)
        for i in range(int(min(X)), int(max(X))):
            for j in range(int(min(Y)), int(max(Y))):
                parite = 0
                for k in range(n):
                    parite += are_intersecting(i,j,X[k],Y[k],X[(k+1)%n],Y[(k+1)%n])
                if(parite % 2 == 1) and (parite != 0):
                    map[j,i] = True
        masked_overlay = np.ma.masked_where(~map, map)
        self.delete("all") 
        self.overlay = self.axs[0].imshow(masked_overlay, cmap = "Reds_r", alpha = 0.6, label = f"poly n°{self.overlay_number}")
        self.map = map 
        self.canvas.draw()
        self.button_confirm.clicked.disconnect()
        self.button_confirm.clicked.connect(self.confirm_to_plot)
        self.label.setText("press enter to plot the mean spectrum of the selected shape, and delete to remove everything.")
    

    def confirm_to_plot(self):
        # Plot the mean spectrum of the selected cluster 
        print("Plotting")
        
        self.axs[1].plot(self.wavelengths,mean_spectre_of_cluster(self.map, self.data_img,True), label = f"poly n°{self.overlay_number}")
        self.delete("overlay")
        self.canvas.draw("legend")
        self.overlay_number+=1
        self.label.setText("Click to add points, right-click to remove the last point, press enter to confirm the polygon, and delete to remove everything.")


    def delete(self, what):
        # Delete the overlay and/or points and/or lines from the image shown
        print("Deleting")
        self.button_confirm.clicked.disconnect()
        self.button_confirm.clicked.connect(self.confirm_to_connect)
        
        if what == "all" or what == "overlay":
            if self.overlay is not None:
                # self.overlay.remove()
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
            n = len(self.line_plots)
            if n != 0:
                print("   - lines deleted")
                for i in range(n):
                    self.line_plots[i].remove()
                self.line_plots = []
        self.canvas.draw()



if __name__ == "__main__":
    resized = Signal(int,int)
    app = QApplication(sys.argv)
    window = MainWindow_draw_cluster(resized)
    window.show()
    sys.exit(app.exec())

    def resizeEvent(self, event):
        """ Emits the signal when the window is resized """
        # width, height = event.size().width(), event.size().height()
        # self.resized.emit(width, height)  # Emit signal with new size
        self.resized.emit()
        super().resizeEvent(event)



