import subprocess
from io import BytesIO
import tempfile
import os
from shutil import rmtree

import pyglet
from pyglet.gl import *  # noqa F403


class Movie:
    """A movie is an instance of ved that acts as a container for layers"""

    def __init__(self, width: int, height: int, background=(0, 0, 0, 1)):
        self.width = width
        self.height = height
        self.background = background

        self._tracks = Movie.Tracks(self)
        # Create opengl context (wrapped in an invisible window).
        # This will be used to render the final result.
        self._window = pyglet.window.Window(
            width=width, height=height, visible=False)
        self.current_time = 0.0

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

    def _reset(self):
        for track in self.tracks:
            self._reset_track(track)

    def _reset_track(self, track):
        start_time, layer = track
        layer.active = False    # Clear active flag directly

    def _process_track(self, track, time):
        start_time, layer = track
        end_time = start_time + layer.duration
        if start_time <= time < end_time:
            if not layer.active:
                layer.start()
            layer.render(time - start_time)
        else:
            if layer.active:
                layer.stop()

    def _process_tracks(self, time):
        for track in self.tracks:
            self._process_track(track, time)

    def _draw(self):
        glClearColor(*self.background)
        glClear(GL_COLOR_BUFFER_BIT)

    def _render(self, time):
        self._process_tracks(time)
        self._draw()

    def tick(self):
        """Call each node"""
        # TODO: Update all nodes once nodes are implemented

    def play(self, start_time: float, end_time: float,
    frame_rate: float):
        """Call each node periodically from `start_time` to `end_time`"""

        self.current_time = start_time
        while self.current_time <= end_time:
            self.tick()
            self.current_time += 1.0 / frame_rate

    def screenshot(self, time, filename, file=None):
        """
        Save a screenshot of the movie to a file or file-like object

        :param float time: the time in seconds to take a screenshot at
        :param str filename: where to write the file, or hint of output format
        :param file: file-like object to write to, optional
        :type file: typing.IO, optional
        """
        self._render(time)

        pyglet.image.get_buffer_manager() \
            .get_color_buffer() \
            .get_image_data() \
            .save(filename=filename, file=file)

    def _prepare_record_command(self, fps, format, audio, tmp):
        # Since ffmpeg has a hard time with multiple piped inputs, only pipe
        # images and save the audio to temporary files.
        cmd = 'ffmpeg -r {} -f png_pipe -i pipe: '.format(fps)
        audio_id = 0
        for _, audio_data in audio:
            clip_path = os.path.join(tmp, 'audio_{}.wav'.format(audio_id))
            with open(clip_path, 'wb') as f:
                f.write(audio_data)
            cmd += '-f wav -i {} '.format(clip_path)
            audio_id += 1
        cmd += '-c:v libx264 -c:a aac -pix_fmt yuv420p -crf 23 -r {} ' \
            .format(fps)
        cmd += '-y -f {} -movflags frag_keyframe+empty_moov '.format(format)
        cmd += '-max_interleave_delta 0 pipe: -v error'
        return cmd

    def record(self, filename, fps, file=None):
        """Render the movie from `start_time` to `end_time`"""

        close_file = False   # close the file when done if we created it here
        if file is None:
            file = open(filename, 'wb')
            close_file = True
        format = filename[filename.rfind('.') + 1:]
        tmp = tempfile.mkdtemp(prefix='ved-')

        # TODO: populate with tuples (clip, data) for each output audio node
        audio = []
        screenshots = BytesIO()
        self.current_time = 0  # TODO: replace with start_time
        while self.current_time <= self.duration:  # TODO: use end_time
            self.tick()
            # TODO: render video nodes to movie
            self.screenshot(self.current_time, 'frame.png', file=screenshots)
            # TODO: render video nodes to movie
            for clip, data in audio:
                # if clip has output, append it to data
                pass
            self.current_time += 1.0 / fps

        cmd = self._prepare_record_command(fps, format, audio, tmp)
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate(input=screenshots.getvalue())

        rmtree(tmp)

        if stderr:
            raise RuntimeError('Error running `{}`:\n{}'.format(cmd, stderr))
        file.write(bytes(stdout))
        if close_file:
            file.close()

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
