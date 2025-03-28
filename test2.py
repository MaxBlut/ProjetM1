import sys
import spectral as sp
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
from time import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QLineEdit
)

from test3 import CustomWidgetRangeSlider

import re

import os      

class KMeansApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Means Clustering on HDR Images")
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)  # Définir le widget central de la fenêtre

        # Double slider
        self.slider_widget = CustomWidgetRangeSlider()
        layout = QVBoxLayout(central_widget)

        layout.addWidget(self.slider_widget)  #  Fix: Removed `layout.layout()`
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMeansApp()
    window.show()
    sys.exit(app.exec())