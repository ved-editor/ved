from .node import Node


class Audio(Node):
    """Base class for all nodes that contains audio"""

    def __init__(self, start_time: float, end_time: float, sample_size: int,
    sample_rate: int, output=False):
        """
        Create an audio node

        :param output: Include video (and audio) output in movie
        :type output: bool, optional
        """

        super().__init__(start_time, end_time)
        self.sample_size = sample_size
        self.sample_rate = sample_rate
        self.output = output

        self.sample = 0.0  # placeholder value

    def __call__(self, movie):
        """
        Calculate a single audio sample and stores it in `self.sample`
        """
