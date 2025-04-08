import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QTabWidget, QStyleFactory


from Save_Import import Save_import
from Double_Curseur import Double_Curseur
from Trois_Slider import Trois_Slider
from Image_Mode_Slider import Image_Mode_Slider
from main_dessin_cluster import MainWindow_draw_cluster
from vegetation_indices_GPU import veget_indices_GPU
from main_double_kmean_sklearn import KMeansApp

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appli curseur")
        self.showMaximized()
        self.save_import = Save_import()
        initial_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Image en couleur par défaut

        self.save_import.matplotlib_widgets = []
        self.matplotlib_widget_rgb = Image_Mode_Slider(initial_image)
        self.save_import.matplotlib_widgets.append(self.matplotlib_widget_rgb)

        self.matplotlib_widget_double = Double_Curseur(initial_image)
        self.save_import.matplotlib_widgets.append(self.matplotlib_widget_double)

        self.matplotlib_widget_3slid = Trois_Slider(initial_image)
        self.save_import.matplotlib_widgets.append(self.matplotlib_widget_3slid)

        self.widget_drawcluster = MainWindow_draw_cluster()
        self.save_import.matplotlib_widgets.append(self.widget_drawcluster)

        self.widget_veget_i = veget_indices_GPU()
        self.save_import.matplotlib_widgets.append(self.widget_veget_i)

        self.widget_KMeansApp = KMeansApp()
        self.save_import.matplotlib_widgets.append(self.widget_KMeansApp)


        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()

        self.tabs.addTab(self.tab1, "Accueil")
        self.tabs.addTab(self.tab2, "Unique WL")
        self.tabs.addTab(self.tab3, "Plage WL")
        self.tabs.addTab(self.tab4, "RGB-3sliders")
        self.tabs.addTab(self.tab5, "Draw cluster")
        self.tabs.addTab(self.tab6, "Indices")
        self.tabs.addTab(self.tab7, "Kmean")

        self.save_import.import_button.clicked.connect(self.loading_file)


        layout = QHBoxLayout()
        layout.addWidget(self.save_import)
        self.tab1.setLayout(layout)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.matplotlib_widget_rgb)
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(self.matplotlib_widget_double)
        self.tab3.setLayout(layout3)

        layout4 = QVBoxLayout() 
        layout4.addWidget(self.matplotlib_widget_3slid)
        self.tab4.setLayout(layout4)

        layout5 = QVBoxLayout() 
        layout5.addWidget(self.widget_drawcluster)
        self.tab5.setLayout(layout5)

        layout6 = QVBoxLayout() 
        layout6.addWidget(self.widget_veget_i)
        self.tab6.setLayout(layout6)

        layout7 = QVBoxLayout() 
        layout7.addWidget(self.widget_KMeansApp)
        self.tab7.setLayout(layout7)


        self.setCentralWidget(self.tabs)
        

    def loading_file(self):
        """ Load the file and update the widgets """
        for widget in self.save_import.matplotlib_widgets:
            widget.load_file(self.save_import.file_path_noload, self.save_import.wavelength, self.save_import.data_img)
        





def set_dark_theme(app):
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))

    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setStyle("Fusion")
    app.setPalette(dark_palette)




if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    print(QStyleFactory.keys())
    set_dark_theme(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())