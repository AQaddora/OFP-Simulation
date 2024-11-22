# ofp_interface.py

import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox, QCheckBox,
    QVBoxLayout, QTextEdit, QSizePolicy, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import ofp_simulation
import matplotlib.pyplot as plt


class AspectRatioWidget(QWidget):
    def __init__(self, widget, aspect_ratio=1, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.aspect_ratio = aspect_ratio
        layout = QHBoxLayout(self)
        layout.addWidget(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        # Calculate the size to maintain aspect ratio
        if w / h > self.aspect_ratio:
            # Too wide, adjust width
            w = int(h * self.aspect_ratio)
        else:
            # Too tall, adjust height
            h = int(w / self.aspect_ratio)
        self.widget.resize(w, h)
        super().resizeEvent(event)


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        # Set the figure size to be square
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.aspect_ratio = 1.0

    def plot_network(self, node_dict, message_id, transmission_range, threshold,
                     transmitting_nodes, non_transmitting_nodes, not_received_nodes, source_node_id, area):
        area_width = math.sqrt(area)
        # Clear the figure to reset the plot
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Separate positions for different categories
        tx_x = []
        tx_y = []
        rx_only_x = []
        rx_only_y = []
        not_rx_x = []
        not_rx_y = []
        tx_node_ids = []

        for node in node_dict.values():
            x, y = node.position
            if message_id in node.transmitted:
                tx_x.append(x)
                tx_y.append(y)
                tx_node_ids.append(node.id)
                # Draw transmission range circle
                circle = plt.Circle((x, y), transmission_range, color='red', fill=False, linestyle='--', alpha=0.2)
                ax.add_artist(circle)
            elif message_id in node.distance_to_nearest_tx:
                rx_only_x.append(x)
                rx_only_y.append(y)
            else:
                not_rx_x.append(x)
                not_rx_y.append(y)

            # Annotate node IDs
            ax.text(x - 3, y - 3, str(node.id), fontsize=6).set_color('yellow')

        # Plot nodes with different colors
        ax.scatter(tx_x, tx_y, c='red', label='Transmitted', s=100)
        ax.scatter(rx_only_x, rx_only_y, c='green', label='Received Only', s=70)
        ax.scatter(not_rx_x, not_rx_y, c='blue', label='Did Not Receive', s=50)

        # Highlight the source node
        if source_node_id in tx_node_ids:
            index = tx_node_ids.index(source_node_id)
            ax.scatter([tx_x[index]], [tx_y[index]], c='black', s=120, label='Source Node')

        # Set axis limits to ensure the plot is square
        x_min, x_max = -area_width / 2 - 25, area_width / 2 + 25
        y_min, y_max = -area_width / 2 - 25, area_width / 2 + 25
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Set aspect ratio to 'equal' to make the plot square
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True)

        # Draw the canvas
        self.draw()


class OFPSimulationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create labels and line edits
        area_width_label = QLabel('Area Width:')
        self.area_width_input = QLineEdit()
        self.area_width_input.setText('600')

        area_label = QLabel('Area (squared):')
        self.area_input = QLineEdit()
        self.area_input.setText(str(float(self.area_width_input.text()) ** 2))  # Calculate initial area
        self.area_input.setReadOnly(True)  # Disable area input
        self.area_input.setStyleSheet("background-color: black;")  # Optional: Gray out the field

        # Connect the area_width_input to update_area method
        self.area_width_input.textChanged.connect(self.update_area)

        nodes_count_label = QLabel('Number of Nodes:')
        self.nodes_count_input = QLineEdit()
        self.nodes_count_input.setText('50')  # Default value

        R_label = QLabel('Transmission Range (R):')
        self.R_input = QLineEdit()
        self.R_input.setText('100')  # Default value

        Th_label = QLabel('Threshold Ratio (Th/R):')
        self.Th_input = QLineEdit()
        self.Th_input.setText('0.4')  # Default value (0.4 * R)

        # Add a checkbox for isRandom
        self.is_random_checkbox = QCheckBox("Random Distribution")
        self.is_random_checkbox.setChecked(False)  # Default is grid distribution

        # Run Simulation Button
        run_button = QPushButton('Run Simulation')
        run_button.clicked.connect(self.on_run_simulation)

        # Layout setup for inputs
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        input_layout.addWidget(area_width_label, 1, 0)
        input_layout.addWidget(self.area_width_input, 1, 1)

        input_layout.addWidget(area_label, 2, 0)
        input_layout.addWidget(self.area_input, 2, 1)

        input_layout.addWidget(nodes_count_label, 3, 0)
        input_layout.addWidget(self.nodes_count_input, 3, 1)

        input_layout.addWidget(R_label, 4, 0)
        input_layout.addWidget(self.R_input, 4, 1)

        input_layout.addWidget(Th_label, 5, 0)
        input_layout.addWidget(self.Th_input, 5, 1)

        input_layout.addWidget(self.is_random_checkbox, 6, 0, 1, 2)  # Add the checkbox to the layout

        input_layout.addWidget(run_button, 7, 0, 1, 2)

        # Set up text areas for node ID arrays
        self.transmitted_text = QTextEdit()
        self.transmitted_text.setReadOnly(True)
        self.transmitted_text.setMaximumHeight(100)

        self.received_text = QTextEdit()
        self.received_text.setReadOnly(True)
        self.received_text.setMaximumHeight(100)

        self.not_received_text = QTextEdit()
        self.not_received_text.setReadOnly(True)
        self.not_received_text.setMaximumHeight(100)

        # Labels for text areas
        transmitted_label = QLabel('Transmitted Nodes:')
        transmitted_label.setStyleSheet("color: red; font-weight: bold;")

        received_label = QLabel('Received Only Nodes:')
        received_label.setStyleSheet("color: green; font-weight: bold;")

        not_received_label = QLabel('Did Not Receive Nodes:')
        not_received_label.setStyleSheet("color: blue; font-weight: bold;")

        # Layout for text areas
        text_layout = QVBoxLayout()
        text_layout.addWidget(transmitted_label)
        text_layout.addWidget(self.transmitted_text)
        text_layout.addWidget(received_label)
        text_layout.addWidget(self.received_text)
        text_layout.addWidget(not_received_label)
        text_layout.addWidget(self.not_received_text)

        # Threshold and Transmission Range Labels
        self.params_label = QLabel(f"Threshold Ratio (Th/R):\nTransmission Range (R):\nDelivery ratio:\nSaved transmissions:")
        self.params_label.setAlignment(Qt.AlignLeft)

        # Left layout combines input_layout, params_label, and text_layout
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(input_layout)
        left_layout.addWidget(self.params_label)
        left_layout.addLayout(text_layout)

        # Set up the plot canvas
        self.plot_canvas = PlotCanvas(self, width=5, height=5)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_canvas.updateGeometry()

        # Wrap the plot_canvas in AspectRatioWidget
        self.plot_widget = AspectRatioWidget(self.plot_canvas, aspect_ratio=1.0)

        # Use a QSplitter to split left and right sections
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.plot_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 500])

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.setWindowTitle('Optimized Flooding Protocol Simulation')
        self.setGeometry(100, 100, 935, 600)
        self.show()
        self.on_run_simulation()

    def update_area(self):
        try:
            area_width = float(self.area_width_input.text())
            area = area_width ** 2
            self.area_input.setText(str(area))
        except ValueError:
            self.area_input.setText('Invalid')

    def on_run_simulation(self):
        try:
            area_width = float(self.area_width_input.text())
            area = area_width ** 2
            nodes_count = int(self.nodes_count_input.text())
            transmission_range = float(self.R_input.text())
            threshold_ratio = float(self.Th_input.text())
            threshold = threshold_ratio * transmission_range
            is_random = self.is_random_checkbox.isChecked()

            # Run the simulation
            (node_dict, message_id, transmitting_nodes, non_transmitting_nodes,
             not_received_nodes, transmission_range, threshold_value, source_node_id) = ofp_simulation.simulate_ofp(
                transmission_range, threshold, area, nodes_count, is_random
            )

            # Update the plot
            self.plot_canvas.plot_network(node_dict, message_id, transmission_range, threshold_value,
                                          transmitting_nodes, non_transmitting_nodes, not_received_nodes, source_node_id, area)

            # Update the parameters label
            count = len(transmitting_nodes) + len(non_transmitting_nodes) + len(not_received_nodes)
            delivery_ratio = (1 - (len(not_received_nodes) - 1) / count) * 100
            saved_transmissions = (len(non_transmitting_nodes) / count) * 100
            self.params_label.setText(f"Threshold Ratio (Th/R): {threshold_ratio}\nTransmission Range (R): {transmission_range}\nDelivery ratio: {delivery_ratio:.2f}%\nSaved transmissions: {saved_transmissions:.2f}%")

            # Update the text areas
            self.transmitted_text.setText(', '.join(map(str, sorted(transmitting_nodes))))
            self.received_text.setText(', '.join(map(str, sorted(non_transmitting_nodes))))
            self.not_received_text.setText(', '.join(map(str, sorted(not_received_nodes))))

        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter valid numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Qt5Agg')

    app = QApplication(sys.argv)
    ex = OFPSimulationApp()
    sys.exit(app.exec_())
