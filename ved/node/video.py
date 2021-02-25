import pyglet

from .node import Node


class Video(Node):
    """Base class for all nodes that contains audio"""

    def __init__(self, start_time: float, end_time: float, x: int, y: int,
    width: int, height: int, output_video=True):
        """
        Create a video node

        :param output_video: Include video output in movie
        :type output_video: bool, optional
        """

        super().__init__(start_time, end_time)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.output_video = output_video

        # Create an opengl context for rendering this node
        self.window = pyglet.window.Window(
            width=width, height=height, visible=False)

    def __call__(self, movie):
        """
        Render a single video frame to `self.window`
        """

        self.window.switch_to()
