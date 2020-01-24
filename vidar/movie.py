import pyglet


class Movie:
    """A movie is an instance of Vidar that acts as a container for layers"""

    def __init__(self, width: int, height: int, background=(0, 0, 0, 1)):
        self.width = width
        self.height = height
        self.background = background

        self._window = pyglet.window.Window(
            width=width, height=height, visible=False)
