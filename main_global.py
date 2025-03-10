import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel
from main_dessin_cluster import MatplotlibImage


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
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Initialize a dictionary to keep track of created tabs
        self.created_tabs = {}

    def on_tab_changed(self, index):
        if index == 0 and index not in self.created_tabs:
            self.setup_tab1()
            self.created_tabs[index] = True
        elif index == 1 and index not in self.created_tabs:
            self.setup_tab2()
            self.created_tabs[index] = True
        elif index == 2 and index not in self.created_tabs:
            self.setup_tab3()
            self.created_tabs[index] = True

    def setup_tab1(self):
        wlMin = 402
        R = round((700-wlMin)/2) 
        G = round((550-wlMin)/2)
        B = round((450-wlMin)/2)
        data = sp.open_image("feuille_250624_ref.hdr").load()
        RGB_img = data[:,:,(R,G,B)]
        if RGB_img.max()*2 < 1:
            RGB_img *= 2
        layout = QVBoxLayout()
        all = MatplotlibImage(RGB_img, data)
        layout.addWidget(all)
        self.tab1.setLayout(layout)

    def setup_tab2(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 2")
        layout.addWidget(label)
        self.tab2.setLayout(layout)

    def setup_tab3(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 3")
        layout.addWidget(label)
        self.tab3.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
