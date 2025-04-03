import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vispy import scene
from vispy.scene import visuals

class VisPy3DGrid(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Create a VisPy canvas (GPU-rendered)
        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
        layout.addWidget(self.canvas.native)

        # Create a 3D view
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'  # Interactive 3D rotation

        # Generate 3D grid data
        x = np.linspace(-5, 5, 50)  # 50x50 grid
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)  # Example surface

        # Flatten arrays for Mesh
        X_flat, Y_flat, Z_flat = X.flatten(), Y.flatten(), Z.flatten()

        # Create face indexes for Mesh grid
        rows, cols = X.shape
        faces = []
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Create two triangles per square
                idx1 = i * cols + j
                idx2 = i * cols + (j + 1)
                idx3 = (i + 1) * cols + j
                idx4 = (i + 1) * cols + (j + 1)

                faces.append([idx1, idx2, idx3])  # First triangle
                faces.append([idx2, idx4, idx3])  # Second triangle

        faces = np.array(faces, dtype=np.uint32)

        # Define colors based on Z height (smooth gradient)
        color_scale = (Z_flat - Z_flat.min()) / (Z_flat.max() - Z_flat.min())  # Normalize
        colors = np.column_stack((color_scale, np.zeros_like(color_scale), 1 - color_scale, np.ones_like(color_scale)))

        # Create Mesh object
        self.mesh = visuals.Mesh(vertices=np.column_stack((X_flat, Y_flat, Z_flat)), 
                                 faces=faces, shading='smooth')

        self.view.add(self.mesh)  # Add to scene

        # Set up event handler for clicking on a point
        self.canvas.events.mouse_press.connect(self.on_mouse_click)

        # Window settings
        self.setWindowTitle("GPU-Accelerated 3D Mesh with Click-to-Focus")
        self.resize(800, 600)


    def on_mouse_click(self, event):
        """ Dynamically move the camera to focus on a clicked point. """
        if event.button == 3:  # midle-click only
            pos = event.pos  # Get mouse position
            picked = self.view.scene.node_transform(self.mesh).map(pos)  # Map to scene coords
            if picked is not None:
                self.view.camera.center = (picked[:3][0],picked[:3][1],0)  # Move camera to the clicked point
                print(f"Centered on: {picked[:3]}")  # Debugging


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VisPy3DGrid()
    window.show()
    sys.exit(app.exec_())
