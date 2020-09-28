class Layer:
    """A layer is a piece of content for the movie"""

    def __init__(self, duration):
        self.duration = duration
        self.enabled = True
        self.active = False
        self._movie = None

    def attach(self, movie):
        """Bind this layer to a movie"""

        self._movie = movie

    def detach(self):
        """Separate this layer from the currently-attached movie"""

        if not self._movie:
            return  # not attached
        self._movie = None

    def start(self):
        """Activate the layer"""

        self.active = True

    def render(self, time):
        """
        Draw any visual content to pyglet

        :param float time: the time of the current frame relative to the layer
        """

    def sample(self, time):
        """
        Return the audio sample at a particular time

        :param float time: the time of the current frame relative to the layer
        """

    def stop(self):
        """Deactivate the layer"""

        self.active = False
