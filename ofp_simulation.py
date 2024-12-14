import math
import heapq
import itertools
import random
from config import Config

epsilon = 1e-6  # To get rid of precise floating-point issues


# Helper functions
def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def strategic_points(center):
    """Calculate the strategic points (vertices of a hexagon) around a center."""
    points = []
    for angle_deg in range(0, 360, 60):
        angle_rad = math.radians(angle_deg)
        x = center[0] + Config.transmission_range * math.cos(angle_rad)
        y = center[1] + Config.transmission_range * math.sin(angle_rad)
        points.append((x, y))
    return points


class Node:
    def __init__(self, node_id, position):
        self.id = node_id
        self.position = position
        self.neighbors = []
        self.transmitted = set()
        self.distance_to_nearest_tx = {}

    def add_neighbor(self, neighbor):
        """Add a neighboring node within the transmission range."""
        self.neighbors.append(neighbor)

    def receive_message(self, message_id, L2, from_node, current_time, event_queue, event_id_counter, source_position):
        """Handle receiving a message."""
        if message_id in self.transmitted:
            return  # Already transmitted this message

        # Update distance to nearest transmitting node
        dn = self.distance_to_nearest_tx.get(message_id, float('inf'))
        dist_to_sender = distance(self.position, from_node.position)
        if dist_to_sender < dn:
            self.distance_to_nearest_tx[message_id] = dist_to_sender
            dn = dist_to_sender

        # Check if the message should be discarded
        if dn < Config.get_threshold():
            return

        # Calculate delay based on distance and strategic points
        if from_node.position == source_position:
            hex_center = source_position
        else:
            hex_center = L2

        l = min(distance(self.position, sp) for sp in strategic_points(hex_center))
        d = l / (Config.transmission_range if from_node.position == source_position else 20 * Config.transmission_range)

        # Schedule transmission after delay d
        transmission_time = current_time + d
        event_id = next(event_id_counter)
        heapq.heappush(event_queue, (transmission_time, event_id, self.transmit_message, message_id, source_position))

    def transmit_message(self, message_id, source_position, event_queue, current_time, event_id_counter):
        """Transmit a message to neighbors."""
        if message_id in self.transmitted:
            return

        self.transmitted.add(message_id)
        self.distance_to_nearest_tx[message_id] = 0  # Reset dn

        for neighbor in self.neighbors:
            neighbor.receive_message(message_id, self.position, self, current_time, event_queue, event_id_counter, source_position)


def setup_network():
    """Set up the network using global parameters from Config."""
    # Update Config with results
    Config.transmitting_nodes = []
    Config.non_transmitting_nodes = []
    Config.not_received_nodes = []
    
    transmission_range = Config.transmission_range
    area = Config.set_area(Config.area_width)
    node_count = Config.node_count
    is_random = Config.is_random

    nodes = []
    node_dict = {}
    width = height = math.sqrt(area)
    id_counter = 1

    if is_random:
        for id_counter in range(1, node_count + 1):
            pos = (random.uniform(-width / 2, width / 2),
                   random.uniform(-height / 2, height / 2))
            node_dict[id_counter] = Node(id_counter, pos)
            nodes.append(node_dict[id_counter])
    else:
        hex_height = transmission_range / 2 * math.sqrt(3)
        x_offset = -width / 2
        y_offset = -height / 2
        y = 0.0
        row_number = 0

        while y + y_offset <= height / 2:
            x_shift = (row_number % 2) * (transmission_range / 2)
            x = 0.0
            while x + x_offset <= width / 2:
                if id_counter > node_count:
                    break
                x_pos = x + x_shift + x_offset
                y_pos = y + y_offset
                if -width / 2 <= x_pos <= width / 2 and -height / 2 <= y_pos <= height / 2:
                    pos = (x_pos, y_pos)
                    node_dict[id_counter] = Node(id_counter, pos)
                    nodes.append(node_dict[id_counter])
                    id_counter += 1
                x += transmission_range
            y += hex_height
            row_number += 1
        
        Config.strategicLast = id_counter
        # Fill remaining nodes randomly if necessary
        while id_counter <= node_count:
            pos = (random.uniform(-width / 2, width / 2),
                   random.uniform(-height / 2, height / 2))
            node_dict[id_counter] = Node(id_counter, pos)
            nodes.append(node_dict[id_counter])
            id_counter += 1
    
    for node in nodes:
        for other_node in nodes:
            if node != other_node and distance(node.position, other_node.position) <= transmission_range + epsilon:
                node.add_neighbor(other_node)

    Config.nodes = node_dict


def send_new_message():
    """Send a new message."""
    # Reset node states
    for node in Config.nodes.values():
        node.transmitted.clear()  # Clear transmitted messages
        node.distance_to_nearest_tx.clear()  # Reset nearest transmitter distances

    # Reset Config states
    Config.transmitting_nodes = []
    Config.non_transmitting_nodes = []
    Config.not_received_nodes = []
    
    event_queue = []
    current_time = 0.0
    event_id_counter = itertools.count()

    # Select a source node
    if Config.is_random:
        index = random.randint(1, Config.node_count - 1)
        source_node = Config.nodes[index]
    else:
        index = random.randint(1, Config.strategicLast - 1) # when having 600*600 area calculate this
        source_node = Config.nodes[index]

    Config.message_id = f'msg{random.randint(1, 1000)}'  # Unique message ID
    Config.source_node_id = source_node.id
    L2 = source_node.position

    # Mark the source node as transmitted
    source_node.transmitted.add(Config.message_id)

    # Broadcast message to neighbors
    for neighbor in source_node.neighbors:
        neighbor.receive_message(Config.message_id, L2, source_node, current_time, event_queue, event_id_counter, source_node.position)

    # Process the event queue
    while event_queue:
        current_time, _, function, *args = heapq.heappop(event_queue)
        function(*args, event_queue=event_queue, current_time=current_time, event_id_counter=event_id_counter)

    # Update Config with results
    Config.transmitting_nodes = [node.id for node in Config.nodes.values() if Config.message_id in node.transmitted]
    Config.non_transmitting_nodes = [node.id for node in Config.nodes.values()
                                    if Config.message_id in node.distance_to_nearest_tx and Config.message_id not in node.transmitted]
    Config.not_received_nodes = [node.id for node in Config.nodes.values() if Config.message_id not in node.distance_to_nearest_tx]
