import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QLineEdit, QInputDialog
from config import Config

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100, on_run_send=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.node_positions = {}  # Map positions to node IDs
        self.mpl_connect("button_press_event", self.on_click)  # Add click event handler
        self.on_run_send_callback = on_run_send  # Save the callback reference

    def plot_network(self):
        """Plots the network simulation result."""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.node_positions = {}  # Reset node positions

        # Separate positions for different categories
        tx_x, tx_y = [], []
        rx_only_x, rx_only_y = [], []
        not_rx_x, not_rx_y = [], []
        tx_node_ids = []

        # Initialize min/max coordinates for dynamic axis scaling
        all_x, all_y = [], []

        for node in Config.nodes.values():
            x, y = node.position
            all_x.append(x)
            all_y.append(y)

            self.node_positions[(x, y)] = node.id  # Map position to node ID

            if Config.message_id in node.transmitted:
                tx_x.append(x)
                tx_y.append(y)
                tx_node_ids.append(node.id)
                # Draw transmission range circle
                circle = plt.Circle((x, y), Config.transmission_range, color='red', fill=False, linestyle='--', alpha=0.1)
                self.ax.add_artist(circle)
            elif Config.message_id in node.distance_to_nearest_tx:
                rx_only_x.append(x)
                rx_only_y.append(y)
            else:
                not_rx_x.append(x)
                not_rx_y.append(y)

            # Annotate node IDs in the center of the node and topics underneath
            self.ax.text(
                x, y,  # Centered ID
                f"{node.id}",
                color='white',
                fontsize=7,
                ha='center',
                va='center'
            )
            topics_label = ",".join(node.subscribed_topics)  # Format topics
            self.ax.text(
                x, y - 17,  # Offset the label below the node
                topics_label,
                fontsize=5,
                ha='center',
                va='top'
                # bbox=dict(facecolor='white', alpha=0.6, edgecolor='none')
            )

        # Plot nodes with different colors
        self.ax.scatter(tx_x, tx_y, c='red', alpha=0.4, label='Transmitted', s=150)
        self.ax.scatter(rx_only_x, rx_only_y, c='green',alpha=0.4, label='Received Only', s=150)
        self.ax.scatter(not_rx_x, not_rx_y, c='blue',alpha=0.4, label='Did Not Receive', s=150)

        # Highlight the source node
        if Config.source_node_id in tx_node_ids:
            index = tx_node_ids.index(Config.source_node_id)
            self.ax.scatter([tx_x[index]], [tx_y[index]], c='black', s=200, label='Source Node')

        # Set dynamic axis limits to fit all nodes with inner margins
        padding = 5  # Padding around the plot
        inner_margin = Config.transmission_range / 2 + 10  # Additional inner margin
        x_min, x_max = min(all_x) - padding - inner_margin, max(all_x) + padding + inner_margin
        y_min, y_max = min(all_y) - padding - inner_margin, max(all_y) + padding + inner_margin
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        # Set aspect ratio to 'equal' to make the plot square
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.grid(True)

        # Place the legend outside the plot
        self.ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.15),  # Move the legend below the plot
            ncol=2,  # Arrange legend items in two columns
            fontsize='medium'
        )

        # Use tight_layout to minimize white space
        self.fig.tight_layout(pad=2.0, h_pad=1.0, w_pad=1.0)
        self.draw()

    def on_click(self, event):
        """Handle click events to edit node topics."""
        if event.inaxes != self.ax:
            return

        # Find the closest node to the click position
        clicked_x, clicked_y = event.xdata, event.ydata
        closest_node = None
        closest_distance = float('inf')

        for (x, y), node_id in self.node_positions.items():
            dist = math.sqrt((clicked_x - x) ** 2 + (clicked_y - y) ** 2)
            if dist < closest_distance:
                closest_distance = dist
                closest_node = Config.nodes[node_id]

        # If a node was clicked, show a dialog to edit topics
        if closest_node and closest_distance <= 10:  # Allow a small tolerance for clicks
            self.edit_node_topics(closest_node)

    def edit_node_topics(self, node):
        """Open a dialog to edit a node's subscribed topics."""
        current_topics = ",".join(node.subscribed_topics)

        # Show input dialog for topics
        new_topics, ok = QInputDialog.getText(
            self.parent(),
            f"Edit Topics for Node {node.id}",
            "Enter topics (comma-separated):",
            QLineEdit.Normal,
            current_topics
        )

        if ok:
            # Update the node's topics and redraw the plot
            node.subscribed_topics = [topic.strip() for topic in new_topics.split(",") if topic.strip()]
            # Trigger the parent to resend the message and update the metrics
            self.on_run_send_callback()
