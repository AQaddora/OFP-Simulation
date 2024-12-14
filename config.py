class Config:
    """Global configuration and state for simulation parameters."""
    epsilon = 1e-6 # To get rid off percise floating point issues..
    topics = ["H", "E", "L", "O"]
    # Parameters
    transmission_range = 100
    threshold_ratio = 0.4
    area_width = 600  # Width of the area (not squared)
    node_count = 50
    is_random = False

    # Simulation State
    nodes = {}  # Dictionary of nodes
    transmitting_nodes = []
    non_transmitting_nodes = []
    not_received_nodes = []
    message_id = None
    source_node_id = None
    strategicLast = 0
    
    @classmethod
    def set_area(cls, width):
        """Set the area and calculate the square value."""
        cls.area_width = width
        return cls.area_width ** 2

    @classmethod
    def get_threshold(cls):
        """Calculate and return the threshold based on the threshold ratio."""
        return cls.threshold_ratio * cls.transmission_range
