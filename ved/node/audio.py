from .node import Node


class Audio(Node):
    """Base class for all nodes that contains audio"""

    def __init__(self, start_time: float, end_time: float, channels: int,
    sample_size: int, output_audio=True):
        """
        Create an audio node

        :param output_audio: Include audio output in movie
        :type output_audio: bool, optional
        """

        super().__init__(start_time, end_time)
        self.channels = channels
        self.sample_size = sample_size
        self.output_audio = output_audio

        self.samples = (0.0,) * self.channels  # placeholder value

    def __call__(self, movie):
        """
        Calculate a single audio sample and stores it in `self.sample`
        """
