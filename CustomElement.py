import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolButton, QButtonGroup
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox

from matplotlib.legend import Legend

class CustomToolbar(NavigationToolbar):
    """Custom Matplotlib Toolbar with Two Toggle Buttons (Can Be Unchecked)"""
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.parent = parent
        # Create Toggle Buttons
        self.mean_spctr_point_button = QToolButton(self)
        self.mean_spctr_point_button.setCheckable(True)
        self.mean_spctr_point_button.setIcon(QIcon("i-remade-that-hamster-meme-into-my-rat-v0-cercyjvmn3kb1.jpg"))  # Replace with your image
        self.mean_spctr_point_button.setToolTip("plot_mean_spctr_point")
        
        # Button Group (Allow Manual Unchecking)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(False)  # Allows unchecking
        self.button_group.addButton(self.mean_spctr_point_button)

        # Insert buttons on the LEFT side of the toolbar
        self.insertWidget(self.actions()[0], self.mean_spctr_point_button)

        self.canvas.mpl_connect("button_press_event",self.on_click)


    def on_click(self, event):
        # Handle mouse click events.
        if self.mean_spctr_point_button.isChecked():
            if self.parent.data_img is not None:
                if event.inaxes == self.parent.axs[0]:  # Check if click is on the left graph
                    if event.xdata is not None and event.ydata is not None:
                        
                        x, y = int(event.xdata), int(event.ydata)
                        data = self.parent.data_img[y,x,:].reshape(1,-1)
                        self.parent.axs[1].plot(self.parent.wavelengths, data[0] , label=f"Point ({x}, {y})")

                        self.parent.legend_obj.remove()  # Remove the previous legend
                        _, labels = self.parent.axs[1].get_legend_handles_labels()
                        legend = PickableLegend(self.parent.axs[1],self.parent.canvas, self.parent.axs[1].get_lines(), labels)
                        self.parent.legend_obj = self.parent.axs[1].add_artist(legend)
                        # on récupere la ligne n°-1 (la derniere) de la légende du graphique de droite
                        
                        self.parent.canvas.draw()  # Update the figure




class PickableLegend(Legend):
    """Custom Legend that enables picking on legend items by default."""
    # Store the original legend lines and their corresponding plot lines
    def __init__(self, parent_ax, canvas, *args, **kwargs):
        super().__init__(parent_ax, *args, **kwargs)
        self.parent_canvas = canvas  # Store reference to the parent canvas
        self.parent_ax = parent_ax  # Store reference to the parent axes

        # Enable picking for all legend items
        self._enable_picking()
        self.parent_canvas.mpl_connect("pick_event", self.on_pick)

    def _enable_picking(self):
        """Enable picking for all legend lines."""
        for leg_line in self.get_lines():
            leg_line.set_picker(True)  # Enable clicking on legend items
            leg_line.set_pickradius(8)  # Make it easier to click

    def on_pick(self, event):
        #Handles pick events to toggle visibility of spectra.
        legend = event.artist
        isVisible = legend.get_visible()
        if event.mouseevent.button == 1:    # Left-click toggles visibility
            # Toggle visibility of the corresponding plot
            for legend_obj, line_obj in zip(self.get_lines(),self.parent_ax.get_lines()):
                if legend_obj == legend:
                    legend.set_visible(not isVisible)
                    line_obj.set_visible(not isVisible)
                    
        elif event.mouseevent.button == 3:  # Right-click opens deletion prompt
            for legend_obj, line_obj in zip(self.get_lines(),self.parent_ax.get_lines()):
                if legend_obj == legend:
                    if messagebox.askyesno("Delete Line", f"Do you want to delete {legend}?"):
                        #legend_obj.remove()
                        line_obj.remove()
        self.parent_canvas.draw()

