import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox, QCheckBox,
    QVBoxLayout, QSizePolicy, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from config import Config
import ofp_simulation
from plot_network import PlotCanvas  # Import the PlotCanvas


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
        if w / h > self.aspect_ratio:
            w = int(h * self.aspect_ratio)
        else:
            h = int(w / self.aspect_ratio)
        self.widget.resize(w, h)
        super().resizeEvent(event)


class OFPSimulationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create labels and line edits
        area_width_label = QLabel('Area Width:')
        self.area_width_input = QLineEdit(str(Config.area_width))

        area_label = QLabel('Area (squared):')
        self.area_input = QLineEdit(str(Config.set_area(Config.area_width)))
        self.area_input.setReadOnly(True)

        # Connect the area_width_input to update_area method
        self.area_width_input.textChanged.connect(self.update_area)

        nodes_count_label = QLabel('Number of Nodes:')
        self.nodes_count_input = QLineEdit(str(Config.node_count))

        R_label = QLabel('Transmission Range (R):')
        self.R_input = QLineEdit(str(Config.transmission_range))

        Th_label = QLabel('Threshold Ratio (Th/R):')
        self.Th_input = QLineEdit(str(Config.threshold_ratio))

        self.is_random_checkbox = QCheckBox("Random Distribution")
        self.is_random_checkbox.setChecked(Config.is_random)
        
        setup_button = QPushButton('Re-setup network')
        setup_button.clicked.connect(self.on_run_setup)
        setup_button.clicked.connect(self.remove_focus)
        
        send_button = QPushButton('Send new message')
        send_button.clicked.connect(self.on_run_send)
        send_button.clicked.connect(self.remove_focus)

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
        input_layout.addWidget(self.is_random_checkbox, 6, 0, 1, 2)
        input_layout.addWidget(setup_button, 7, 0, 1, 2)
        input_layout.addWidget(send_button, 8, 0, 1, 2)

        # Metrics label
        self.params_label = QLabel()
        self.params_label.setAlignment(Qt.AlignLeft)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(input_layout)
        left_layout.addWidget(self.params_label)

        # Plot canvas
        self.plot_canvas = PlotCanvas(self, width=5, height=5)
        self.plot_widget = AspectRatioWidget(self.plot_canvas, aspect_ratio=1.0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.plot_widget)
        splitter.setStretchFactor(1, 1)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.setWindowTitle('Optimized Flooding Protocol Simulation')
        self.setGeometry(100, 100, 935, 600)
        self.show()
        self.on_run_setup()

    def remove_focus(self):
        self.area_width_input.clearFocus()
        self.nodes_count_input.clearFocus()
        self.R_input.clearFocus()
        self.Th_input.clearFocus()
        self.setFocus()  # Set focus to the main window or parent


    def update_area(self):
        try:
            area_width = float(self.area_width_input.text())
            area = Config.set_area(area_width)
            self.area_input.setText(str(area))
        except ValueError:
            self.area_input.setText('Invalid')

    def on_run_send(self):
        """Send new message."""
        try:
            # Run the simulation (no return values needed)
            ofp_simulation.send_new_message()

            # Plot the results from Config
            self.plot_canvas.plot_network(
                Config.nodes,
                Config.message_id,
                Config.transmission_range,
                Config.get_threshold(),
                Config.transmitting_nodes,
                Config.non_transmitting_nodes,
                Config.not_received_nodes,
                Config.source_node_id,
                Config.area_width ** 2
            )

            # Calculate metrics
            total_nodes = Config.node_count
            received_nodes = len(Config.transmitting_nodes) + len(Config.non_transmitting_nodes)
            not_received_nodes = len(Config.not_received_nodes) - 1
            delivery_ratio = (received_nodes / total_nodes) * 100 if total_nodes else 0
            saved_transmissions = (len(Config.non_transmitting_nodes) / total_nodes) * 100 if total_nodes else 0

            # Update the metrics label
            self.params_label.setText(
                f"\nMetrics:\n"
                f"Delivery Ratio: {delivery_ratio:.2f}%\n"
                f"Saved Transmissions: {saved_transmissions:.2f}%\n"
                f"Nodes that did not receive: {not_received_nodes}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_run_setup(self):
        """Update Config and run the simulation."""
        try:
            # Update Config parameters from user input
            Config.area_width = float(self.area_width_input.text())
            Config.node_count = int(self.nodes_count_input.text())
            Config.transmission_range = float(self.R_input.text())
            Config.threshold_ratio = float(self.Th_input.text()) - Config.epsilon
            Config.is_random = self.is_random_checkbox.isChecked()
            Config.nodes = []
            
            # Re-setup the network
            ofp_simulation.setup_network()
            self.on_run_send()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OFPSimulationApp()
    sys.exit(app.exec_())
