import sys
from superqt import QRangeSlider, QLabeledSlider
from PySide6.QtWidgets import QApplication

# Initialiser QApplication
app = QApplication(sys.argv)

# Créer un range slider
range_slider = QRangeSlider()
range_slider.setRange(0, 100)
range_slider.setValue((25, 75))
range_slider.show()

# Créer un slider avec des labels
labeled_slider = QLabeledSlider()
labeled_slider.setRange(0, 100)
labeled_slider.setValue(50)
labeled_slider.show()

sys.exit(app.exec())
