import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_network(self, node_dict, message_id, transmission_range, threshold,
                     transmitting_nodes, non_transmitting_nodes, not_received_nodes, source_node_id, area):
        """Plots the network simulation result."""
        area_width = math.sqrt(area)
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Separate positions for different categories
        tx_x, tx_y = [], []
        rx_only_x, rx_only_y = [], []
        not_rx_x, not_rx_y = [], []
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
        ax.legend(loc='upper right')
        self.draw()
