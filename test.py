import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QComboBox, QLabel

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sélecteur de Fichier avec Extension")
        self.setGeometry(100, 100, 400, 200)

        # Label pour afficher le fichier sélectionné
        self.label = QLabel("Aucun fichier sélectionné", self)

        # Bouton pour ouvrir le sélecteur de fichier
        self.button = QPushButton("Choisir un fichier", self)
        self.button.clicked.connect(self.open_file_dialog)

        # Menu déroulant pour choisir l'extension
        self.combo_box = QLabel(".hdr")

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.combo_box)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        self.setLayout(layout)


    def open_file_dialog(self):
        # Récupérer l'extension sélectionnée

        # Ouvrir le sélecteur de fichier
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", self.combo_box.text() + " Files (*" + self.combo_box.text() + ")")

        # Mettre à jour le label avec le chemin sélectionné
        if file_path:
            self.label.setText(f"Fichier sélectionné:\n{file_path}")
        else:
            self.label.setText("Aucun fichier sélectionné")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSelector()
    window.show()
    sys.exit(app.exec_())
