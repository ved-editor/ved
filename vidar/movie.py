# pylint: disable=missing-module-docstring

class Movie:
    """A movie is an instance of Vidar that acts as a container for layers"""
    def __init__(self, width: int, height: int, background=(0, 0, 0, 1)):
        self.width = width
        self.height = height
        self.background = background
