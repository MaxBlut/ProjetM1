import sys
from PySide6.QtWidgets import QToolButton,QVBoxLayout,QLabel,QComboBox,QPushButton, QDialog,QApplication,QDialogButtonBox,QHBoxLayout,QWidget,QFileDialog,QMainWindow, QInputDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from tkinter import messagebox
from qtpy.QtCore import Qt
import spectral as sp
sp.settings.envi_support_nonlowercase_params = True

from matplotlib.legend import Legend
from matplotlib.patches import Patch

from utiles import mean_spectre_of_cluster, set_legend, get_legend, custom_clear

from superqt import QRangeSlider

from time import time













class CustomQRangeSlider(QRangeSlider):
    """Custom QRangeSlider that emits a signal when the slider is released."""
    sliderReleased = Signal(tuple)  # Define a custom signal that sends the slider values

    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        """Initialize with the specified orientation (default: Horizontal)."""
        super().__init__(orientation, parent)  # Pass orientation to the parent class


    def mouseReleaseEvent(self, event):
        """Detects when the user releases the slider and emits the custom signal."""
        super().mouseReleaseEvent(event)  # Call the default behavior
        self.sliderReleased.emit(self.value())  # Emit signal with the current values



class CustomWidgetRangeSlider(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.wavelenghts = [i for i in range(10)]
        layout = QHBoxLayout(self)
        

        self.wl_min_label = QLabel() 
        layout.addWidget(self.wl_min_label)
        self.range_slider = CustomQRangeSlider()
        layout.addWidget(self.range_slider)
        self.wl_max_label = QLabel() 
        layout.addWidget(self.wl_max_label)

        self.setRange(self.wavelenghts)
        self.update_label((0,len(self.wavelenghts)-1))
        self.range_slider.setValue((0,len(self.wavelenghts)-1))


        self.range_slider.valueChanged.connect(self.update_label)

    def update_label(self, value):
        """Update labels and restrict slider movement to allowed values."""
        
        min_index, max_index = value  # Get slider positions
        min_value, max_value = float(self.wavelenghts[min_index]), float(self.wavelenghts[max_index])  # Map indices to values
        self.wl_min_label.setText("{}".format(min_value))
        self.wl_max_label.setText("{}".format(max_value))
        """Reduit l'étude des clustering aux valeurs indiqués"""

    def setRange(self, wavelenghts):
        if wavelenghts:
            self.range_slider.setRange(0,len(wavelenghts)-1)
        else :
            print("WARNING : wavelenght is None in CustomWidgetRangeSlider.setRange(",wavelenghts ,")")
            self.range_slider.setRange(0,10)

    def setWavelenghts(self,wavelenghts):
        self.wavelenghts = wavelenghts
        self.setRange(self.wavelenghts) #update the range
        self.range_slider.setValue((0,len(wavelenghts)-1))

class CommentButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent	
        self.comment_text = ""  # Stocker le commentaire

        self.comment = QPushButton("Commenter pour sauvegarde")
        self.comment.clicked.connect(self.commenter)

        layout = QVBoxLayout()
        layout.addWidget(self.comment)
        self.setLayout(layout)

    def commenter(self):
        text, ok = QInputDialog.getMultiLineText(self, "Ajouter un commentaire pour la sauvegarde globale", "Entrez votre commentaire :")
        if ok and text:
            self.parent.text = text  # Stocker le texte dans l'attribut
            print(f"Commentaire ajouté : {text}")  # Debug

    def get_comment(self):
        return self.comment_text  # Getter pour récupérer le commentaire




class CustomToolbar(NavigationToolbar):
    """Custom Matplotlib Toolbar with Two Toggle Buttons (Can Be Unchecked)"""
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)

        self.parent = parent
        self.left_mouse_pressed = False
        self.right_mouse_pressed = False
        self.selected_pixels_map = None
        self.number_of_overlay_ploted = 0
        self.overlay = None

        # Create mean_spctr_point_button Buttons
        self.mean_spctr_point_button = QToolButton(self)
        self.mean_spctr_point_button.setCheckable(True)
        self.mean_spctr_point_button.setIcon(QIcon("photo/point.png")) 
        self.mean_spctr_point_button.setToolTip("plot the mean spectrum of the clicked point")
        self.mean_spctr_point_button.clicked.connect(self.toggle_mean_spctr_point)

        # Create pen_button Buttons
        self.pen_button = QToolButton(self)
        self.pen_button.setCheckable(True)
        self.pen_button.setIcon(QIcon("photo/pen.jpg"))
        self.pen_button.setToolTip("select pixels with the pen using left mouse button and remove them with the right mouse button.\n " \
                                    "Click the middle mouse button or enter to plot the mean spectrum of the selected pixels.")
        self.pen_button.clicked.connect(self.toggle_pen)

        #create merge buttons
        self.merge_clusters_button = QToolButton(self)
        self.merge_clusters_button.setIcon(QIcon("photo/merge.jpg")) 
        self.merge_clusters_button.setToolTip("Merge Clusters")
        self.merge_clusters_button.clicked.connect(self.open_merge_window)


        # Insert buttons on the LEFT side of the toolbar
        self.insertWidget(self.actions()[0], self.pen_button)
        self.insertWidget(self.actions()[0], self.mean_spctr_point_button)
        self.insertWidget(self.actions()[-1], self.merge_clusters_button)
       
        # Connecte les nouveaux et certains anciens boutons de la toolbar au fonctions 
        self.canvas.mpl_connect("button_press_event",self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self._actions['zoom'].triggered.connect(self.zoom_toggled)
        self._actions['pan'].triggered.connect(self.pan_toggled)

        # Find the "Edit Axis" button in the toolbar
        self.edit_axes_action = self._actions.get("edit_parameters")

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


    def hook_edit_axis_dialog(self):
        """Hooks into the Edit Axis dialog and connects the Apply button to update the legend."""
        # print("Edit Axis dialog opened!")
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
        if self.overlay is not None:
                    self.overlay.remove()
                    self.overlay = None


    def on_click(self, event):
        # Handle mouse click events.
        # Check if the mean spectrum point button is checked
        if self.mean_spctr_point_button.isChecked():
            if self.parent.data_img is not None:
                if event.inaxes == self.parent.axs[0]:  # Check if click is on the left graph
                    if event.xdata is not None and event.ydata is not None:
                        x, y = int(event.xdata), int(event.ydata)
                        data = self.parent.data_img[y,x,:].reshape(1,-1)
                        self.parent.axs[1].plot(self.parent.croped_wavelength, data[0] , label=f"Point ({x}, {y})")
                        self.parent.canvas.draw("legend")  # Update the figure


        # Check if the pen button is checked
        if self.pen_button.isChecked():
            if self.parent.data_img is not None: # Check if an image is loaded
                if event.inaxes == self.parent.axs[0]: # Check if click is on the left graph
                    if event.button == 1: # clic gauche
                        self.left_mouse_pressed = True
                    elif event.button == 2: # clic milieu
                        self.plot_overlay()
                    elif event.button == 3: # clic droit
                        self.right_mouse_pressed = True
        

    def plot_overlay(self):
        # compute and plot the mean spetra of the drawn pixels
        avg_spectrum = mean_spectre_of_cluster(self.selected_pixels_map, self.parent.data_img, selected_cluster_value=True)
        if avg_spectrum[0] >= 0: # on fait ce if pour qu'il ne ce passe rien dans le cas ou l'utilisateur valide le plot sans avoir selectionné de pixels
            cmap = plt.get_cmap("nipy_spectral")
            norm = plt.Normalize(0, self.number_of_overlay_ploted+1)
            color = cmap(norm(self.number_of_overlay_ploted))
            self.number_of_overlay_ploted +=1
            self.parent.axs[1].plot(self.parent.croped_wavelength, avg_spectrum,color=color, label=f"groupe n°{self.number_of_overlay_ploted}")                           
            # remove overlay and empty the selected pixels map
            # self.overlay.remove()
            self.overlay = None
            self.selected_pixels_map[:,:] = False
            self.parent.canvas.draw("legend")


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
        """fonction utilisé pour gerer les evenements lors de l'utilisation de la fonction crayon """
        # Triggered when the mouse button is released.
        if self.left_mouse_pressed or self.right_mouse_pressed:
            if event.button == 3 or event.button == 1:
                if self.overlay is not None:
                    self.overlay.remove()
                    self.overlay = None
                cmap = plt.get_cmap("nipy_spectral")
                norm = plt.Normalize(0, self.number_of_overlay_ploted+1)
                color = cmap(norm(self.number_of_overlay_ploted))
                masked_overlay = np.ma.masked_where(~self.selected_pixels_map, self.selected_pixels_map)
                self.overlay = self.parent.axs[0].imshow(masked_overlay, colorizer=color, alpha = 0.9,label=f"groupe n°{self.number_of_overlay_ploted+1}")
                self.overlay.set_cmap(plt.cm.colors.ListedColormap([color]))
                self.parent.canvas.draw()
        if self.left_mouse_pressed and event.button == 1:
            self.left_mouse_pressed = False  # Stop recording           
        elif self.right_mouse_pressed and event.button == 3:
            self.right_mouse_pressed = False 


    


















class PickableLegend(Legend):
    """Custom Legend that enables picking on legend items, including both lines and images."""
    
    def __init__(self, parent_ax, canvas, plot_objects, labels, *args, **kwargs):
        """
        plot_objects: List of either Line2D or AxesImage objects to be controlled by the legend.
        labels: Corresponding labels for each plot object.
        """
        self.parent_canvas = canvas
        self.parent_ax = parent_ax
        self.plot_objects = plot_objects  # Store reference to lines & images

        
        # Convert AxesImage objects into proxy patches
        self.proxies = [self.create_proxy(obj, lbl) if isinstance(obj, matplotlib.image.AxesImage) else obj
                        for obj, lbl in zip(plot_objects, labels)]

        # Call Legend constructor with the new proxy list
        super().__init__(parent_ax, handles=self.proxies, labels=labels, *args, **kwargs)
        
        self._enable_picking()
        self._pick_event_id = self.parent_canvas.mpl_connect("pick_event", self.on_pick)
        set_legend(self.parent_ax, self)


    def create_proxy(self, image, label):
        """Creates a colored box proxy for an image to use in the legend."""
        color = image.cmap(image.norm(image.get_array().mean()))  # Estimate color from image
        return Patch(color=color, label=label)


    def _enable_picking(self):
        """Enable picking for legend items."""
        for leg_item in self.legend_handles:  # legend_handles contains both lines & image proxies
            leg_item.set_picker(True)
            if isinstance(leg_item, matplotlib.lines.Line2D):  # Apply pickradius only to lines
                leg_item.set_pickradius(8)  # Increase click tolerance


    def on_pick(self, event):
        if event.mouseevent is not None:
            event.mouseevent.handled = True  # Mark event as handled to prevent propagation

        """Handles pick events to toggle visibility for both 2D lines and images."""
        legend_item = event.artist  # Clicked legend item
        
        if event.mouseevent.button == 1:  # Left-click toggles visibility
            for legend_obj, plot_obj in zip(self.legend_handles, self.plot_objects):
                if legend_obj == legend_item:
                    is_visible = plot_obj.get_visible()
                    legend_obj.set_visible(not is_visible)
                    plot_obj.set_visible(not is_visible)
                    # print(f"Toggled visibility for: {plot_obj.get_label()}")
                    
                    self.parent_ax.draw_artist(legend_obj)
                    self.parent_ax.draw_artist(plot_obj)

                    self.parent_canvas.draw_idle()  # Forces refresh 
                    break
        
        elif event.mouseevent.button == 3:  # Right-click opens deletion prompt
            for legend_obj, plot_obj in zip(self.legend_handles, self.plot_objects):
                if legend_obj == legend_item:
                    obj_label = plot_obj.get_label()  # Get label directly
                    if messagebox.askyesno("Delete Item", f"Do you want to delete {obj_label}?"):
                        plot_obj.remove()
                        print(f"Deleted: {obj_label}")
                        self.parent_canvas.draw("legend")
                    break
        


    

    


























class CustomCanvas(FigureCanvas):
    # a custom canvas that include the custom pickable legend with a modified draw methode 
    def __init__(self, figure, parent_axs):
        super().__init__(figure)
        self.parent_axs = parent_axs


    def draw(self, what = None):
        """Overrides Matplotlib's draw method to execute custom code before drawing."""
        if what == "legend":
            self.update_legend()  # Execute custom function
        super().draw()  # Proceed with the normal drawing


    def update_legend(self):
        """Updates the legend be removing and reploting it."""
        
        for i in range(len(self.parent_axs)):
            plot_list = []
            label_list = []
            number_img = 0
            for children in self.parent_axs[i].get_children():
                if type(children) is matplotlib.lines.Line2D:
                    plot_list.append(children)
                    label_list.append(children.get_label())
                elif  type(children) is matplotlib.image.AxesImage :
                    number_img+=1
                    if number_img > 1:
                        plot_list.append(children)
                        label_list.append(children.get_label())
        

            legend_obj = get_legend(self.parent_axs[i])
            if legend_obj:
                self.mpl_disconnect(legend_obj._pick_event_id)
                legend_obj.remove()
                set_legend(self.parent_axs[i], None)


            if len(label_list)>0:
                legend_obj = PickableLegend(self.parent_axs[i], self, plot_list, label_list)
                set_legend(self.parent_axs[i], legend_obj)
                self.parent_axs[i].add_artist(legend_obj)
        
        








class hyperspectral_appli(QWidget):

    def display_image(self):
        if self.data_img is not None:
            custom_clear(self.axs[0])
            if self.WL_MIN <= 450:
                R = round((700-self.WL_MIN)/2) 
                G = round((550-self.WL_MIN)/2)        #to do : modifier le calcule d'indice pour ne plus avoir a diviser par deux 
                B = round((450-self.WL_MIN)/2)
                RGB_img = self.data_img[:,:,(R,G,B)]

                if RGB_img.max()*2 < 1:
                    try:
                        RGB_img = 2*RGB_img.view(np.ndarray)
                    except ValueError:
                        pass
                self.axs[0].imshow(RGB_img)
            else:
                print("RGB values not supported")
            self.axs[0].axis('off')
            self.axs[0].set_title("hyperspectral image")
            self.canvas.draw()
    

    def load_file(self):
        """charge le fichié selectionné par l'utilisateur """
        
        self.variable_init()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier HDR", "", "HDR Files (*.hdr)")
        if self.file_path:
            if hasattr(self, "file_label"):
                self.file_label.setText(f"Fichier : {self.file_path}")
            self.extract_hdr_info()
            # print(self.file_path, " selected")
        for ax in self.axs:
            custom_clear(ax)
        # self.axs[1].set_title("spectrum")
        self.display_image()
        if hasattr(self, "slider_widget"):
            self.slider_widget.setWavelenghts(self.original_wavelengths)
        self.canvas.draw()
    
    
    def extract_hdr_info(self):
        """Extract wlMin, wlMax and the wavelength list from an ENVI header file."""
        img = sp.open_image(self.file_path)
        self.data_img = img.load()

        if 'wavelength' in img.metadata:
            self.original_wavelengths = img.metadata['wavelength']
        elif "Wavelength" in img.metadata:
            self.original_wavelengths = img.metadata['Wavelength']
        else:
            print("wavelength metadata not found")
            return
        # print("metadata found")
        self.original_wavelengths = [float(i) for i in self.original_wavelengths]
            
        self.croped_wavelength = self.original_wavelengths
        self.wl_max_cursor = self.croped_wavelength[-1]
        self.wl_min_cursor = self.croped_wavelength[0]
        self.WL_MIN = self.wl_min_cursor