# Optimized Flooding Protocol (OFP) Simulation
<p align="center">
  <img width="500" height="auto" src="./media/ofp_simulation.png">
</p>


A Python implementation and simulation of the **Optimized Flooding Protocol (OFP)** for wireless ad-hoc networks, based on the original paper: [Optimized Flooding Protocol for Ad-hoc Networks](https://arxiv.org/pdf/cs/0311013).

This project provides a simulation environment to study the behavior of the OFP algorithm in wireless networks. It allows users to adjust various parameters, visualize the network topology, and observe how messages propagate through the network using OFP.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Simulation](#command-line-simulation)
  - [Graphical Interface](#graphical-interface)
- [Parameters](#parameters)
- [Visualization](#visualization)
- [Example Output](#example-output)
- [Reference](#reference)
- [Contributing](#contributing)
- [TODO](#todo)
- [License](#license)

---

## Features

- Simulates the **Optimized Flooding Protocol** in wireless ad-hoc networks.
- Visualizes network topology and message propagation.
- Adjustable parameters for area size, node count, transmission range, and threshold.
- Supports both random and grid-based node distribution.
- Graphical User Interface (GUI) using PyQt5 for interactive simulations.
- Displays key statistics like delivery ratio and saved transmissions.

---

## Installation

### Prerequisites

- **Python 3.x**
- **pip** (Python package installer)

### Required Python Packages

Install the required packages using pip:

```bash
pip install PyQt5 matplotlib
```

---

## Usage

### Command-Line Simulation

Run the simulation from the command line using the `test_simulation.py` script. You can specify the simulation parameters as command-line arguments:

```bash
python test_simulation.py --area_width 600 --nodes_count 65 --transmission_range 100 --threshold_ratio 1 --is_random False
```

#### Arguments:

- `--area_width`: (Default: `600`) Width and height of the square simulation area. The total area is calculated as `area_width^2`.
- `--nodes_count`: (Default: `65`) Number of nodes in the network.
- `--transmission_range`: (Default: `100`) Transmission range of each node.
- `--threshold_ratio`: (Default: `1.0`) Threshold ratio relative to the transmission range. **Internally, this value is slightly decreased by a small `epsilon` (e.g., `1e-6`) to account for floating-point precision issues.** For example, a threshold ratio of `1` means the actual threshold used in the simulation is slightly less than the transmission range, ensuring accurate transmission eligibility.
- `--is_random`: (Default: `False`) Whether to use random node distribution (`True`) or grid-based distribution (`False`).

**Note:** If arguments are omitted, the script will use the default values.

#### Examples:

1. **Using Default Values:**

   ```bash
   python test_simulation.py
   ```

   This will execute the simulation with:
   - `area_width = 600`
   - `nodes_count = 65`
   - `transmission_range = 100`
   - `threshold_ratio = 1.0`
   - `is_random = False`

2. **Specifying a Custom Number of Nodes:**

   ```bash
   python test_simulation.py --nodes_count 80
   ```

   Sets `nodes_count` to `80`, with other parameters using default values.

3. **Changing the Transmission Range and Threshold Ratio:**

   ```bash
   python test_simulation.py --transmission_range 120 --threshold_ratio 0.8
   ```

   Sets `transmission_range` to `120` and `threshold_ratio` to `0.8`.

4. **Placing Nodes Randomly:**

   ```bash
   python test_simulation.py --is_random
   ```

   Sets `is_random` to `True`, placing nodes randomly instead of in a grid pattern.

---

### Graphical Interface

![interface](/media/ofp_interface.png)


For an interactive experience, run the `ofp_interface.py` script:

```bash
python ofp_interface.py
```

The GUI allows you to:

- Set simulation parameters like area width, number of nodes, transmission range, and threshold.
- Choose between random or grid-based node distribution.
- Visualize the network and observe message propagation in real-time.
- View statistics such as delivery ratio and percentage of saved transmissions.

---

## Parameters

- **Area Width (`area_width`)**: The dimensions of the square simulation area. The total area is calculated as `area_width^2`.
- **Number of Nodes (`nodes_count`)**: Total nodes in the network.
- **Transmission Range (`transmission_range`)**: Maximum distance a node can transmit a message.
- **Threshold Ratio (`threshold_ratio`)**: Determines if a node should transmit a received message based on its distance to the nearest transmitting node. **Internally, the threshold is slightly decreased by a small `epsilon` (e.g., `1e-6`) to account for floating-point precision issues.** For example, a `threshold_ratio` of `1` means the actual threshold used is slightly less than the transmission range, ensuring nodes are accurately evaluated for transmission eligibility.
- **Random Distribution (`is_random`)**: If checked, nodes are placed randomly; otherwise, they are placed in a grid pattern.

---

## Visualization

The simulation visualizes the network and message propagation using color-coded nodes:

- **Red Nodes**: Nodes that **transmitted** the message.
- **Green Nodes**: Nodes that **received** the message but did **not transmit**.
- **Blue Nodes**: Nodes that did **not receive** the message.
- **Black Node**: The **source node** that initiated the message.
- **Circles**: Represent the transmission range of transmitting nodes.

---

## Example Output

After running the simulation, you will see:

- A plot of the network with nodes and transmission ranges.
- Statistics such as:
  - **Threshold**: The threshold value used (accounting for epsilon adjustment).
  - **Transmission Range**: The transmission range of nodes.
  - **Delivery Ratio**: Percentage of nodes that received the message.
  - **Saved Transmissions**: Percentage of nodes that received but did not transmit, indicating efficiency.
------
![output](/media/example_output.png)
------

## Reference

This project is based on the following paper:

- **Optimized Flooding Protocol for Ad-hoc Networks**
  - [arXiv:cs/0311013](https://arxiv.org/abs/cs/0311013)

---

## Contributing

Contributions are welcome! Currently, the simulation transmits a message from a random node on the generated network.

To contribute:

1. **Fork the repository.**
2. **Create a new branch** for your feature or bug fix.
3. **Submit a pull request** with detailed information about your changes.

---

## TODO

- Implement **moving nodes** to simulate node mobility.
- Support **transmitting different messages** to mimic real network traffic.
- Introduce **multiple source nodes** to study concurrent transmissions.
- Enhance the GUI with additional controls and real-time statistics.
- Optimize the simulation for larger and more complex networks.

---

## License

[MIT Licence](./LICENCE)
---

**Note**: This project is intended for educational and research purposes, providing insights into the Optimized Flooding Protocol and its impact on network performance.

Feel free to explore, modify, and utilize this simulation to further understand the dynamics of wireless ad-hoc networks and the Optimized Flooding Protocol.

---

**Additional Explanation on Epsilon Adjustment:**

To ensure accurate simulation results, especially when dealing with floating-point precision issues, the threshold value (`Th`) is internally adjusted by subtracting a small epsilon (`epsilon = 1e-6`). This adjustment ensures that nodes are correctly evaluated for transmission eligibility without being erroneously excluded due to minor numerical inaccuracies. For instance, a threshold ratio of `1` implies that the actual threshold used is `transmission_range - epsilon`, effectively mitigating potential floating-point discrepancies.