import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QFileDialog, QComboBox, QLineEdit
)
from PyQt5.QtGui import QPixmap, QImage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Histogram Display")

        # Create graph
        self.canvas = FigureCanvas(plt.Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.set_title('Histogram Display')
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('Frequency')

        # File choose buttons
        self.choose_specs_button = QPushButton("Choose Test Specs File")
        self.choose_specs_button.clicked.connect(self.choose_specs_file)
        self.choose_results_button = QPushButton("Choose Test Results Files")
        self.choose_results_button.clicked.connect(self.choose_results_files)

        # Factor choose combo box
        self.variable_combo_box = QComboBox()
        self.variable_combo_box.currentIndexChanged.connect(self.update_plot)

        #DUT search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search DUT SN")
        self.search_box.setEnabled(False)
        self.search_box.returnPressed.connect(self.search_dut_sn) # search after enter key

        # Layout
        layoutV1 = QVBoxLayout()
        layoutH1 = QHBoxLayout()
        layoutH2 = QHBoxLayout()

        layoutV1.addWidget(self.choose_specs_button)
        layoutV1.addWidget(self.choose_results_button)
        layoutV1.addWidget(self.canvas)
        layoutV1.addWidget(self.variable_combo_box)
        layoutV1.addWidget(self.search_box)

        # Main widget
        central_widget = QWidget()
        central_widget.setLayout(layoutV1)
        self.setCentralWidget(central_widget)

        # variables
        self.specs_df = None
        self.results_df = None
        self.clean_results_data = None
        self.scatter_plot = None

    def choose_specs_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("CSV files (*.csv)")
        file_dialog.fileSelected.connect(self.load_specs_data)
        file_dialog.exec_()

    def choose_results_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("CSV files (*.csv)")
        file_dialog.filesSelected.connect(self.load_results_files)
        file_dialog.exec_()

    def load_specs_data(self, file_path):
        try:
            self.specs_df = pd.read_csv(file_path)
            factors = [col for col in self.specs_df['Test Names'] if col.startswith(("V_", "I_"))]
            self.variable_combo_box.clear()
            self.variable_combo_box.addItems(factors)
        except Exception as e:
            print(f"Error loading specs data: {e}")

    def process_specs(self):
        try:
            factors = [col for col in self.specs_df['Test Names'] if col.startswith(("V_", "I_"))]
            self.variable_combo_box.clear()
            self.variable_combo_box.addItems(factors)
        except Exception as e:
            print(f"Error obtaining specs from spec file. Check if the file is correct: {e}")

    def load_results_files(self, file_paths):
        try:
            dfs = [pd.read_csv(file_path) for file_path in file_paths]
            self.results_df = pd.concat(dfs)
        except Exception as e:
            print(f"Error loading results data: {e}")

    def clean_data(self):
        if self.results_df is not None:
            self.clean_results_data = self.results_df.copy()
            self.clean_results_df = self.clean_results_df.drop_duplicates(subset=['DUT_SN'], keep='last')

    def update_plot(self):
        if self.specs_df is not None and self.results_df is not None:
            selected_factor = self.variable_combo_box.currentText()
            self.ax.clear()
            
            variable = self.results_df[selected_factor].dropna().values
            spec_row = self.specs_df[self.specs_df["Test Names"] == selected_factor]
            variable_USL = pd.to_numeric(spec_row['USL'].iloc[0], errors='coerce')
            variable_LSL = pd.to_numeric(spec_row['LSL'].iloc[0], errors='coerce')
            var_range = variable_USL - variable_LSL
            var_lower_lim = variable_LSL - 0.055263 * var_range
            var_upper_lim = variable_USL + 0.055263 * var_range

            # limit x axis to 1.2x of range of USL - LSL
            self.ax.set_xlim(var_lower_lim, var_upper_lim)

            # Calculate the bin width
            num_bins = 19
            bin_width = var_range / num_bins
            # Calculate the bin edges with regard to xlim
            bin_edges = [variable_LSL + i * bin_width for i in range(num_bins + 1)]
            self.ax.hist(self.results_df[selected_factor], density=True, bins=bin_edges, color='blue', edgecolor='black', alpha=0.7)

            # Draw a vertical line at USL and LSL
            self.ax.axvline(x=variable_LSL, color='red', linestyle='--', linewidth=2, label='_nolegend_')
            self.ax.axvline(x=variable_USL, color='red', linestyle='--', linewidth=2, label='_nolegend_')

            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
            self.search_box.setEnabled(True)  # Enable search box after plotting


    def search_dut_sn(self):
        if self.scatter_plot:
            self.scatter_plot.remove()
        if self.results_df is not None:
            search_text = self.search_box.text()

            if search_text:
                try:
                    print(search_text)
                    dut_sn_index = self.results_df['DUT_SN'].tolist().index(search_text)
                    selected_factor = self.variable_combo_box.currentText()
                    
                    y_min, y_max = self.ax.get_ylim()
                    y_val = (y_max - y_min) / 10 + y_min
                    y_mid = (y_min + y_max) / 2
                    x_value = self.results_df.iloc[dut_sn_index][selected_factor]

                    self.scatter_plot = self.ax.scatter(x_value, y_mid, color='green', marker='v', s=100)
                    self.canvas.draw()
                    
                except ValueError:
                    self.scatter_plot = None
                    self.canvas.draw()
                    print("DUT_SN not found in results_df")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())