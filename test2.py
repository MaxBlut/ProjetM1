import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout
)
from superqt import QRangeSlider
from test3 import CustomWidgetRangeSlider


class KMeansApp(QWidget):  # Hérite maintenant de QWidget
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K-Means Clustering on HDR Images")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Double slider
        self.slider_widget = CustomWidgetRangeSlider()
        layout.addWidget(self.slider_widget)

        self.setLayout(layout)  # Ajout explicite du layout
        self.setGeometry(100, 100, 800, 600)


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = KMeansApp()
    window.show()
    sys.exit(app.exec())
