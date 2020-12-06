import pyglet

from .node import Node


class Video(Node):
    """Base class for all nodes that contains audio"""

    def __init__(self, start_time: float, end_time: float, width: int,
    height: int, output=False):
        """
        Create a video node

        :param output: Include audio (and video) output in movie
        :type output: bool, optional
        """

        super().__init__(start_time, end_time)
        self.width = width
        self.height = height
        self.output = output

        # Create an opengl context for rendering this node
        self.window = pyglet.window.Window(
            width=width, height=height, visible=False)

    def __call__(self, movie):
        """
        Render a single video frame to `self.window`
        """
