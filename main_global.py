import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel
from main_dessin_cluster import MainWindow_draw_cluster
from main_double_kmean_sklearn import KMeansApp

import spectral as sp
sp.settings.envi_support_nonlowercase_params = True



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Multiple Tabs Example")
        self.setGeometry(100, 100, 600, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)  # Set the tab widget as the main widget

        # Create tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        # Add tabs to the QTabWidget
        self.tabs.addTab(self.tab1, "Draw Cluster")
        self.tabs.addTab(self.tab2, "Double KMeans")
        self.tabs.addTab(self.tab3, "Tab 3")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Initialize a dictionary to keep track of created tabs
        self.setup_tab1()

        
    def on_tab_changed(self, index):
        if index == 0:
            self.setup_tab1()
            self.unload_tabs(tab2=True, tab3=True)
        elif index == 1:
            self.setup_tab2()
            self.unload_tabs(tab1=True, tab3=True)
        elif index == 2:
            self.setup_tab3()
            self.unload_tabs(tab1=True, tab2=True)

    def setup_tab1(self):
        layout = QVBoxLayout()
        all = MainWindow_draw_cluster()
        layout.addWidget(all)
        self.tab1.setLayout(layout)

    def setup_tab2(self):
        layout = QVBoxLayout()
        all = KMeansApp()
        layout.addWidget(all)
        self.tab2.setLayout(layout)

    def setup_tab3(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 3")
        layout.addWidget(label)
        self.tab3.setLayout(layout)

    
    def unload_tabs(self, tab1=False, tab2=False, tab3=False):
        if tab1:
            self.tab1.setLayout(None)
        if tab2:
            self.tab2.setLayout(None)
        if tab3:
            self.tab3.setLayout(None)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
