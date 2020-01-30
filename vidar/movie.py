import pyglet
from pyglet.gl import *  # noqa F403


class Movie:
    """A movie is an instance of Vidar that acts as a container for layers"""

    def __init__(self, width: int, height: int, background=(0, 0, 0, 1)):
        self.width = width
        self.height = height
        self.background = background

        self._tracks = Movie.Tracks(self)
        self._window = pyglet.window.Window(
            width=width, height=height, visible=False)

    @property
    def tracks(self):
        return self._tracks

    def add_layer(self, time, layer):
        self.tracks.append((time, layer))
        return self

    def remove_layer(self, layer):
        self.tracks = [(time, layer_) for time, layer_ in self.tracks
            if layer_ != layer]

    @tracks.setter
    def tracks(self, value):
        for time, layer in self.tracks:
            layer.detach()

        self._tracks = Movie.Tracks(self, value)
        for time, layer in value:
            layer.attach(self)

    @property
    def duration(self):
        duration = 0.0
        for time, layer in self.tracks:
            duration = max(duration, time + layer.duration)
        return duration

    def _frame(self, time):
        self._draw()
        self._process_layers(time)

    def _draw(self):
        glClearColor(*self.background)
        glClear(GL_COLOR_BUFFER_BIT)

    def _process_layers(self, time):
        for start_time, layer in self.tracks:
            end_time = start_time + layer.duration
            if start_time <= time < end_time:
                if not layer.active:
                    layer.start()
                layer.frame(time)
            else:
                if layer.active:
                    layer.stop()

    def screenshot(self, time, filename, file=None):
        """Saves a screenshot of the movie to a file or file-like object

        Keyword arguments:
        time -- the time in seconds to take a screenshot at
        filename -- where to write the file, or hint of output format
        file -- file-like object to write to (optional)
        """
        self._frame(time)

        pyglet.image.get_buffer_manager() \
            .get_color_buffer() \
            .get_image_data() \
            .save(filename=filename, file=file)

    class Tracks(list):
        def __init__(self, movie, iterable=()):
            list.__init__(self, iterable)
            self.movie = movie

        def __delitem__(self, track):
            track.detach()
            list.__delitem__(self, track)

        def append(self, track):
            list.append(self, track)
            time, layer = track
            layer.attach(self.movie)
