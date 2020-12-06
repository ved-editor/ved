class Node:
    def __init__(self, start_time: float, end_time: float):
        """Create a new node"""

        self.start_time = start_time
        self.end_time = end_time

    def __call__(self, movie):
        """Execute this node"""
