# test_simulation.py

import argparse
import ofp_simulation

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Optimized Flooding Protocol Simulation')

    # Add arguments with default values
    parser.add_argument('--area_width', type=float, default=600, help='Width and height of the simulation area')
    parser.add_argument('--nodes_count', type=int, default=50, help='Number of nodes in the simulation')
    parser.add_argument('--transmission_range', type=float, default=100, help='Transmission range of the nodes')
    parser.add_argument('--threshold', type=float, default=1.0, help='Threshold ratio relative to the transmission range')
    parser.add_argument('--is_random', action='store_true', help='Set this flag to place nodes randomly')

    # Parse the arguments
    args = parser.parse_args()

    # Set parameters based on arguments or defaults
    area_width = args.area_width
    area = area_width ** 2
    nodes_count = args.nodes_count
    transmission_range = args.transmission_range
    threshold_ratio = args.threshold
    threshold = threshold_ratio * transmission_range
    is_random = args.is_random

    try:
        node_dict, message_id, transmitting_nodes, non_transmitting_nodes, not_received_nodes, transmission_range_value, threshold_value, source_node_id = ofp_simulation.simulate_ofp(
            transmission_range, threshold, area, nodes_count, is_random)
        ofp_simulation.plot_network(
            node_dict, message_id, transmission_range, threshold_value, transmitting_nodes, non_transmitting_nodes, not_received_nodes)
    except KeyboardInterrupt:
        print('')