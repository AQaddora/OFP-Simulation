# ofp_simulation.py

import math
import heapq
import itertools
import matplotlib.pyplot as plt
import random

epsilon = 1e-6 # To get rid off percise floating point issues..

# Helper functions
def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def strategic_points(center, transmission_range):
    """Calculate the strategic points (vertices of a hexagon) around a center."""
    points = []
    for angle_deg in range(0, 360, 60):
        angle_rad = math.radians(angle_deg)
        x = center[0] + transmission_range * math.cos(angle_rad)
        y = center[1] + transmission_range * math.sin(angle_rad)
        points.append((x, y))
    return points

# Node class
class Node:
    def __init__(self, id, position, threshold, transmission_range):
        self.id = id
        self.position = position
        self.neighbors = []
        self.received_messages = {}
        self.transmitted = set()
        self.distance_to_nearest_tx = {}
        self.threshold = threshold
        self.transmission_range = transmission_range

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def receive_message(self, message_id, L1, L2, from_node, current_time, event_queue, event_id_counter, source_position):
        if message_id in self.transmitted:
            return  # Already transmitted this message

        # Update distance to nearest transmitting node
        dn = self.distance_to_nearest_tx.get(message_id, float('inf'))
        dist_to_sender = distance(self.position, from_node.position)
        if dist_to_sender < dn:
            self.distance_to_nearest_tx[message_id] = dist_to_sender
            dn = dist_to_sender

        # Check if should discard the message
        if dn < self.threshold:
            return  # Too close to another transmitter

        # Determine if received directly from source
        if from_node.position == source_position:
            # First-level receivers
            hex_center = source_position
            l = min(distance(self.position, sp) for sp in strategic_points(hex_center, self.transmission_range))
            d = l / self.transmission_range
        else:
            # Subsequent receivers
            hex_center = L2
            l = min(distance(self.position, sp) for sp in strategic_points(hex_center,  self.transmission_range))
            d = l / (20 * self.transmission_range)

        # Schedule transmission after delay d
        transmission_time = current_time + d
        event_id = next(event_id_counter)
        heapq.heappush(event_queue, (transmission_time, event_id, self.transmit_message, message_id, L1, L2, source_position))

    def transmit_message(self, message_id, L1, L2, source_position, event_queue, current_time, event_id_counter):
        if message_id in self.transmitted:
            return  # Already transmitted

        # Update transmitted messages
        self.transmitted.add(message_id)
        self.distance_to_nearest_tx[message_id] = 0  # Reset dn

        # Prepare updated L1 and L2
        new_L1 = L2
        new_L2 = self.position

        # Broadcast to neighbors
        for neighbor in self.neighbors:
            neighbor.receive_message(message_id, new_L1, new_L2, self, current_time, event_queue, event_id_counter, source_position)

# Simulation setup
def setup_network(transmission_range, node_count, area, threshold, is_random):
    nodes = []
    node_dict = {}
    width = height = math.sqrt(area)
    id_counter = 1
    if is_random:
        for id_counter in range(1, node_count + 1):
            pos = (random.uniform(-width / 2, width / 2),
                   random.uniform(-height / 2, height / 2))
            node_dict[id_counter] = Node(
                id_counter, pos, threshold, transmission_range)
            nodes.append(node_dict[id_counter])
    else:
        hex_height = transmission_range /2  * math.sqrt(3)  # Calculated above
        print(f'Hex Height {hex_height}\n\n')
        x_offset = -width / 2
        y_offset = -height / 2

        y = 0.0
        row_number = 0
        while True:
            x_shift = (row_number % 2) * (transmission_range / 2)
            x = 0.0
            if y + y_offset > height / 2:
                break

            while True:
                if id_counter > node_count:
                    break

                x_pos = x + x_shift + x_offset
                y_pos = y + y_offset

                # Break if x position exceeds bounds
                if x_pos > width / 2:
                    break

                # Place the node if it's within the area bounds
                if (-width / 2 <= x_pos <= width / 2) and (-height / 2 <= y_pos <= height / 2):
                    pos = (x_pos, y_pos)
                    node_dict[id_counter] = Node(
                        id_counter, pos, threshold, transmission_range)
                    nodes.append(node_dict[id_counter])
                    id_counter += 1

                x += transmission_range

            y += hex_height
            row_number += 1

            if id_counter > node_count:
                break

        # Fill remaining nodes randomly if necessary
        while id_counter <= node_count:
            pos = (random.uniform(-width / 2, width / 2),
                   random.uniform(-height / 2, height / 2))
            node_dict[id_counter] = Node(
                id_counter, pos, threshold, transmission_range)
            nodes.append(node_dict[id_counter])
            id_counter += 1

    # Establish neighbors
    for node in nodes:
        for other_node in nodes:
            if node != other_node and distance(node.position, other_node.position) <= transmission_range + epsilon:
                node.add_neighbor(other_node)

    return node_dict, len(nodes)




def simulate_ofp(transmission_range, threshold, area, node_count, is_random):
    threshold -= epsilon
    print(f'THRESHOLD ADJUSTED {threshold}')
    node_dict, n = setup_network(transmission_range, node_count, area, threshold, is_random)

    event_queue = []  # Priority queue for events (time, event_id, function, args)
    current_time = 0.0  # Simulation clock
    event_id_counter = itertools.count()

    # Source node sends the initial message
    index = random.randint(1, n-1)
    source_node = node_dict[index]
    message_id = 'msg1'
    L1 = source_node.position
    L2 = source_node.position
    
    source_node.transmitted.add(message_id)

    # Source broadcasts to neighbors
    for neighbor in source_node.neighbors:
        neighbor.receive_message(message_id, L1, L2, source_node, current_time, event_queue, event_id_counter, source_node.position)

    # Process events in the queue
    while event_queue:
        current_time, _, function, *args = heapq.heappop(event_queue)
        function(*args, event_queue=event_queue, current_time=current_time, event_id_counter=event_id_counter)

    # Output results
    print ("Source node that initialized transmision:")
    print (f'{source_node.id} at {source_node.position}')
    
    print("\nNodes that transmitted the message:")
    transmitting_nodes = [node.id for node in node_dict.values() if message_id in node.transmitted]
    print(sorted(transmitting_nodes))

    print("\nNodes that received the message but did not transmit:")
    non_transmitting_nodes = [node.id for node in node_dict.values() if message_id in node.distance_to_nearest_tx and message_id not in node.transmitted]
    print(sorted(non_transmitting_nodes))

    print("\nNodes that did not receive the message:")
    not_received_nodes = [node.id for node in node_dict.values() if message_id not in node.distance_to_nearest_tx]
    print(sorted(not_received_nodes))

    return node_dict, message_id, transmitting_nodes, non_transmitting_nodes, not_received_nodes, transmission_range, threshold, source_node.id

def plot_network(node_dict, message_id, transmission_range, threshold, transmitting_nodes, non_transmitting_nodes, not_received_nodes):
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.set_facecolor('lightgrey')

    # Separate positions for different categories
    tx_x = []
    tx_y = []
    rx_only_x = []
    rx_only_y = []
    not_rx_x = []
    not_rx_y = []

    for node in node_dict.values():
        x, y = node.position
        if message_id in node.transmitted:
            tx_x.append(x)
            tx_y.append(y)
            # Draw transmission range circle
            circle = plt.Circle((x, y), transmission_range, color='r', fill=False, linestyle='--', alpha=0.2)
            ax.add_artist(circle)
        elif message_id in node.distance_to_nearest_tx:
            rx_only_x.append(x)
            rx_only_y.append(y)
        else:
            not_rx_x.append(x)
            not_rx_y.append(y)

        # Annotate node IDs
        ax.text(x + 0.5, y + 0.5, str(node.id), fontsize=8)

    # Plot nodes with different colors
    ax.scatter(tx_x, tx_y, c='red', label='Transmitted', s=100, edgecolors='black')
    ax.scatter(rx_only_x, rx_only_y, c='green', label='Received Only', s=70, edgecolors='black')
    ax.scatter(not_rx_x, not_rx_y, c='blue', label='Did Not Receive', s=50, edgecolors='black')

    # Add legend
    # ax.legend(loc='upper right')

    # Set plot titles and labels
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('Optimized Flooding Protocol Simulation')
    ax.set_aspect('equal', 'box')
    plt.grid(True)

    # Display node ID arrays
    textstr = '\n'.join((
        '\n\n\n\n',
        f'Threshold: {threshold / transmission_range + epsilon:.2f}',
        f'Transmission Range: {transmission_range}',
        f'Delivery ratio: {str((1 - (len(not_received_nodes)-1)/(len(transmitting_nodes) + len(non_transmitting_nodes) + len(not_received_nodes))) * 100)}%'
    ))

    plt.figtext(0.1, 0.02, textstr, fontsize=10, ha='left')

    plt.show()
