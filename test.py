import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from tkinter import messagebox

class PickableLegend:
    def __init__(self, ax, canvas, lines, labels):
        self.ax = ax
        self.canvas = canvas
        self.lines = lines
        self.labels = labels
        self.legend = ax.legend(lines, labels, loc='upper right', fancybox=True, shadow=True, picker=True)
        self.visibility = {line: True for line in lines}  # Track line visibility
        self.canvas.mpl_connect("pick_event", self.on_pick)
    
    def on_pick(self, event):
        legend_item = event.artist
        if isinstance(legend_item, plt.Line2D):
            index = self.labels.index(legend_item.get_label())
            line = self.lines[index]
            
            if event.mouseevent.button == 1:  # Left-click toggles visibility
                visible = not self.visibility[line]
                line.set_visible(visible)
                self.visibility[line] = visible
                legend_item.set_alpha(1.0 if visible else 0.2)  # Dim legend item if hidden
                self.canvas.draw()
            
            elif event.mouseevent.button == 3:  # Right-click opens deletion prompt
                if messagebox.askyesno("Delete Line", f"Do you want to delete {legend_item.get_label()}?"):
                    line.remove()
                    self.lines.pop(index)
                    self.labels.pop(index)
                    self.legend.remove()
                    self.legend = self.ax.legend(self.lines, self.labels, loc='upper right', fancybox=True, shadow=True, picker=True)
                    self.canvas.draw()

def display_spectra(self):
    if self.data_img is not None and self.second_cluster_map is not None:
        self.axs[1].clear()
        self.graph_dict = {}
        cmap = plt.get_cmap("nipy_spectral")
        norm = plt.Normalize(vmin=self.second_cluster_map.min(), vmax=self.second_cluster_map.max())
        plotted_lines = []
        labels = []

        for i in np.unique(self.second_cluster_map):
            mask = self.second_cluster_map == i
            avg_spectrum = np.mean(self.data_img[mask, :], axis=0)
            line, = self.axs[1].plot(self.wavelengths, avg_spectrum, color=cmap(norm(i)), label=f"Cluster {i}")
            plotted_lines.append(line)
            labels.append(f"Cluster {i}")

        legend = PickableLegend(self.axs[1], self.canvas, plotted_lines, labels)
        self.legend_obj = self.axs[1].add_artist(legend)
        self.canvas.draw()
