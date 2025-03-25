import sys
from PySide6.QtWidgets import QToolButton,QVBoxLayout,QLabel,QComboBox,QPushButton, QDialog,QApplication,QDialogButtonBox,QFrame,QBoxLayout
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox

from matplotlib.legend import Legend

from utiles import mean_spectre_of_cluster








class CustomToolbar(NavigationToolbar):
    """Custom Matplotlib Toolbar with Two Toggle Buttons (Can Be Unchecked)"""
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)

        self.parent = parent
        self.left_mouse_pressed = False
        self.right_mouse_pressed = False
        self.selected_pixels_map = None
        self.overlay = None

        # Find the "Edit Axis" button in the toolbar
        self.edit_axes_action = self._actions.get("edit_parameters")
        
        
        

        # Create mean_spctr_point_button Buttons
        self.mean_spctr_point_button = QToolButton(self)
        self.mean_spctr_point_button.setCheckable(True)
        self.mean_spctr_point_button.setIcon(QIcon("i-remade-that-hamster-meme-into-my-rat-v0-cercyjvmn3kb1.jpg")) 
        self.mean_spctr_point_button.setToolTip("plot_mean_spctr_point")
        self.mean_spctr_point_button.clicked.connect(self.toggle_mean_spctr_point)

        # Create pen_button Buttons
        self.pen_button = QToolButton(self)
        self.pen_button.setCheckable(True)
        self.pen_button.setIcon(QIcon("pen.png"))
        self.pen_button.setToolTip("draw on the left graph")
        self.pen_button.clicked.connect(self.toggle_pen)

        
        self.merge_clusters_button = QToolButton(self)
        self.merge_clusters_button.setIcon(QIcon("merge.png")) 
        self.merge_clusters_button.setToolTip("Merge Clusters")
        self.merge_clusters_button.clicked.connect(self.open_merge_window)


        # Insert buttons on the LEFT side of the toolbar
        self.insertWidget(self.actions()[0], self.pen_button)
        self.insertWidget(self.actions()[0], self.mean_spctr_point_button)
        self.insertWidget(self.actions()[-1], self.merge_clusters_button)
       

        self.canvas.mpl_connect("button_press_event",self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self._actions['zoom'].triggered.connect(self.zoom_toggled)
        self._actions['pan'].triggered.connect(self.pan_toggled)
        if self.edit_axes_action:
            self.edit_axes_action.triggered.connect(self.hook_edit_axis_dialog)



    def open_merge_window(self):
        _, self.clusters_labels = self.parent.axs[1].get_legend_handles_labels()
        if self.clusters_labels:
            """Opens a dialog to merge two clusters."""
            self.merge_dialog = QDialog(self.parent)
            self.merge_dialog.setWindowTitle("Merge Clusters")
            layout = QVBoxLayout()

            # Labels
            layout.addWidget(QLabel("Select Cluster 1:"))
            self.cluster1_dropdown = QComboBox()
            layout.addWidget(self.cluster1_dropdown)

            layout.addWidget(QLabel("Select Cluster 2:"))
            self.cluster2_dropdown = QComboBox()
            layout.addWidget(self.cluster2_dropdown)

            # Merge Button
            merge_button = QPushButton("Merge")
            merge_button.clicked.connect(self.merge_clusters)
            layout.addWidget(merge_button)

            # Populate dropdowns with existing clusters
            self.populate_cluster_dropdowns()

            self.merge_dialog.setLayout(layout)
            self.merge_dialog.exec_()

    
    def populate_cluster_dropdowns(self):
        """Fill dropdowns with available cluster names."""
        self.cluster1_dropdown.addItems(self.clusters_labels)
        self.cluster2_dropdown.addItems(self.clusters_labels)


    def merge_clusters(self):
        """Merge two selected clusters into one."""
        label1 = self.cluster1_dropdown.currentText()
        label2 = self.cluster2_dropdown.currentText()
        if label1 and label2 and label1 != label2:
            lines = []
        
            for line, label in zip(self.parent.axs[1].get_lines(), self.clusters_labels):
                if label == label1 or label == label2:
                    lines.append(line)
        
            self.parent.merge_lines(lines)  # Call parent method
            self.merge_dialog.accept()  # Close window





    def pan_toggled(self):
        if self._actions['pan'].isChecked():
            self.pen_button.setChecked(False)
            self.mean_spctr_point_button.setChecked(False)


    def zoom_toggled(self):
        if self._actions['zoom'].isChecked():
            self.pen_button.setChecked(False)
            self.mean_spctr_point_button.setChecked(False)


    def toggle_mean_spctr_point(self):
        if self.mean_spctr_point_button.isChecked():
            if self._actions['zoom'].isChecked():
                self._actions['zoom'].setChecked(False) # this toggle the button off
                self.zoom()  # This properly toggles the zoom off
            if self._actions['pan'].isChecked():
                self._actions['pan'].setChecked(False) # this toggle the button off
                self.pan()  # This properly toggles the pan off
            self.pen_button.setChecked(False)
            
    
    def toggle_pen(self):
        if self.pen_button.isChecked():
            self.mean_spctr_point_button.setChecked(False)
            if self._actions['zoom'].isChecked():
                self._actions['zoom'].setChecked(False) # this toggle the button off
                self.zoom()  # This properly toggles the zoom off
            if self._actions['pan'].isChecked():
                self._actions['pan'].setChecked(False) # this toggle the button off
                self.pan()  # This properly toggles the pan off
            if self.parent.data_img is not None:  #si l'image est chargé 
                if self.selected_pixels_map is None:
                    self.selected_pixels_map = np.full((self.parent.data_img.shape[0], self.parent.data_img.shape[1]), False, dtype=bool)
            else:
                self.pen_button.setChecked(False)






    def on_click(self, event):
        # Handle mouse click events.
        # Check if the mean spectrum point button is checked
        if self.mean_spctr_point_button.isChecked():
            if self.parent.data_img is not None:
                if event.inaxes == self.parent.axs[0]:  # Check if click is on the left graph
                    if event.xdata is not None and event.ydata is not None:
                        
                        x, y = int(event.xdata), int(event.ydata)
                        data = self.parent.data_img[y,x,:].reshape(1,-1)
                        self.parent.axs[1].plot(self.parent.wavelengths, data[0] , label=f"Point ({x}, {y})")
                        self.parent.canvas.draw("legend")  # Update the figure


        # Check if the pen button is checked
        if self.pen_button.isChecked():
            if self.parent.data_img is not None: # Check if an image is loaded
                if event.inaxes == self.parent.axs[0]: # Check if click is on the left graph
                    if event.button == 1: # clic gauche
                        self.left_mouse_pressed = True
                    elif event.button == 2: # clic milieu
                        # compute and plot the mean spetra of the drawn pixels
                        avg_spectrum = mean_spectre_of_cluster(self.selected_pixels_map, self.parent.data_img, selected_cluster_value=True)
                        if avg_spectrum[0] >= 0: # on fait ce if pour qu'il ne ce passe rien dans le cas ou l'utilisateur valide le plot sans avoir selectionné de pixels

                            self.parent.axs[1].plot(self.parent.wavelengths, avg_spectrum, label="groupe de  pixels")
                            
                            # remove overlay and empty the selected pixels map
                            self.overlay.remove()
                            self.overlay = None
                            self.selected_pixels_map[:,:] = False
                            self.parent.canvas.draw("legend")

                    elif event.button == 3: # clic droit
                        self.right_mouse_pressed = True
        

    def on_mouse_move(self, event):
        # Triggered when the mouse moves while pressed.
        if self.left_mouse_pressed and event.inaxes == self.parent.axs[0]:
            x , y = int(event.xdata), int(event.ydata) 
            x = np.array((x,x,x+1,x+1))
            y = np.array((y,y+1,y,y+1))
            self.selected_pixels_map[y,x] = True

        elif self.right_mouse_pressed and event.inaxes == self.parent.axs[0]:
            x , y = int(event.xdata), int(event.ydata) 
            x = np.array((x,x,x+1,x+1))
            y = np.array((y,y+1,y,y+1))
            self.selected_pixels_map[y,x] = False
            

    def on_mouse_release(self, event):
        # Triggered when the mouse button is released.
        if self.left_mouse_pressed or self.right_mouse_pressed:
            if event.button == 3 or event.button == 1:
                if self.overlay is not None:
                    self.overlay.remove()
                    self.overlay = None
                masked_overlay = np.ma.masked_where(~self.selected_pixels_map, self.selected_pixels_map)
                self.overlay = self.parent.axs[0].imshow(masked_overlay, cmap = "Reds_r", alpha = 1)
                self.parent.canvas.draw()

        if self.left_mouse_pressed and event.button == 1:
            self.left_mouse_pressed = False  # Stop recording
            
        elif self.right_mouse_pressed and event.button == 3:
            self.right_mouse_pressed = False 


    def hook_edit_axis_dialog(self):
        """Hooks into the Edit Axis dialog and connects the Apply button to update the legend."""
        print("Edit Axis dialog opened!")

        # Ensure Matplotlib has updated before searching for the dialog
        self.parent.canvas.draw_idle()

        # Loop through all open dialogs
        for dialog in QApplication.instance().topLevelWidgets():
            if isinstance(dialog, QDialog):  # Find the Edit Axis QDialog
                # Find the button box inside the dialog
                button_box = dialog.findChild(QDialogButtonBox)
                if button_box:
                    # Loop through buttons and connect the "Apply" button
                    for button in button_box.buttons():
                        if button.text() == "Apply" or button.text() == "Ok":
                            button.clicked.connect(lambda: self.canvas.draw("legend"))
                            print("Connected Apply button to legend update.")




















class PickableLegend(Legend):
    """Custom Legend that enables picking on legend items by default."""
    # Store the original legend lines and their corresponding plot lines
    def __init__(self, parent_ax, canvas, *args, **kwargs):
        super().__init__(parent_ax, *args, **kwargs)
        self.parent_canvas = canvas  # Store reference to the parent canvas
        self.parent_ax = parent_ax  # Store reference to the parent axes

        # Enable picking for all legend items
        self._enable_picking()

        
        self._pick_event_id = self.parent_canvas.mpl_connect("pick_event", self.on_pick)


        # self.parent_canvas.mpl_connect("pick_event", self.on_pick)


    def _enable_picking(self):
        """Enable picking for all legend lines."""
        for leg_line in self.get_lines():
            leg_line.set_picker(True)  # Enable clicking on legend items
            leg_line.set_pickradius(8)  # Make it easier to click

    def on_pick(self, event):
        #Handles pick events to toggle visibility of spectra.

        if not isinstance(event.artist, plt.Line2D):  # Ignore text & non-line elements
            return
        
        legend = event.artist
        isVisible = legend.get_visible()

        if event.mouseevent.button == 1:    # Left-click toggles visibility
            # Toggle visibility of the corresponding plot
            for legend_obj, line_obj in zip(self.get_lines(),self.parent_ax.get_lines()):
                if legend_obj == legend:
                    legend.set_visible(not isVisible)
                    line_obj.set_visible(not isVisible)
            self.parent_canvas.draw()
                    
        elif event.mouseevent.button == 3:  # Right-click opens deletion prompt
            for legend_obj, line_obj in zip(self.get_lines(),self.parent_ax.get_lines()):
                if legend_obj == legend:
                    if messagebox.askyesno("Delete Line", f"Do you want to delete {legend.get_label()}?"):
                        line_obj.remove()
            self.parent_canvas.draw("legend")
























class CustomCanvas(FigureCanvas):
    def __init__(self, figure, parent_axs):
        super().__init__(figure)
        self.parent_axs = parent_axs
        self.legend_obj = [None for _ in range(len(self.parent_axs))]


    def draw(self, what = None):
        """Overrides Matplotlib's draw method to execute custom code before drawing."""
        if what == "legend":
            self.update_legend()  # Execute custom function
        super().draw()  # Proceed with the normal drawing


    def update_legend(self):
        """Updates the legend be removing and reploting it."""
        
        for i in range(len(self.parent_axs)):
            _, labels = self.parent_axs[i].get_legend_handles_labels()
            # Check if legend already exists
            if self.legend_obj[i] is not None:
                self.mpl_disconnect(self.legend_obj[i]._pick_event_id)
                self.legend_obj[i].remove()
                self.legend_obj[i] = None

            # Create and add the new legend
            if len(labels)>0:
                self.legend_obj[i] = PickableLegend(self.parent_axs[i], self, self.parent_axs[i].get_lines(), labels)
                self.parent_axs[i].add_artist(self.legend_obj[i])
        