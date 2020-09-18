import subprocess
from io import BytesIO
import tempfile
import os
from shutil import rmtree

import pyglet
from pyglet.gl import *  # noqa F403

from .audio import AudioLayer


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

    def screenshot(self, time, filename, file=None):
        """Saves a screenshot of the movie to a file or file-like object

        Keyword arguments:
        time -- the time in seconds to take a screenshot at
        filename -- where to write the file, or hint of output format
        file -- file-like object to write to (optional)
        """
        self._render(time)

        pyglet.image.get_buffer_manager() \
            .get_color_buffer() \
            .get_image_data() \
            .save(filename=filename, file=file)

    def _export_images(self, fps: float) -> bytes:
        """Render the image data of the video as a sequence of file-like
        objects and concatenate them.
        """
        screenshots = BytesIO()
        time = 0.0
        while time < self.duration:
            self.screenshot(time, 'frame.png', file=screenshots)
            time += 1.0 / fps
        return screenshots.getvalue()

    def _export_audio_clips(self) -> list:
        """Sample the audio data of each layer.

        Returns:
            a list of tuples of the form (start_time, audio_data) where
            audio_data is a file-like object
        """
        def has_audio(layer):
            return isinstance(layer, AudioLayer) \
                and layer.audio_format.channels > 0

        return [(time, layer.get_audio_data()) for time, layer in self.tracks
            if has_audio(layer)]

    def _prepare_export_command(self, fps, format, tmp):
        # Since ffmpeg has a hard time with multiple piped inputs, only pipe
        # images and save the audio to temporary files.
        audio_clips = self._export_audio_clips()

        cmd = 'ffmpeg -r {} -f png_pipe -i pipe: '.format(fps)
        audio_id = 0
        for start_time, audio_data in audio_clips:
            clip_path = os.path.join(tmp, 'audio_{}'.format(audio_id))
            with open(clip_path, 'wb') as f:
                f.write(audio_data)
            cmd += '-itsoffset {} -f wav -i {} '.format(start_time, clip_path)
            audio_id += 1
        cmd += '-c:v libx264 -c:a aac -pix_fmt yuv420p -crf 23 -r {} ' \
            .format(fps)
        cmd += '-y -f {} -movflags frag_keyframe+empty_moov '.format(format)
        cmd += '-max_interleave_delta 0 pipe: -v error'
        return cmd

    def export(self, filename, fps, file=None):
        """Render the movie to a file path or a file-like object.

        Keyword arguments:
        filename -- where to write the file, or hint of output format
        fps -- frames per second; note that this does *not* depend on the movie
        file -- file-like object to write to (optional)
        """

        close_file = False   # close the file when done if we created it here
        if file is None:
            file = open(filename, 'wb')
            close_file = True
        format = filename[filename.rfind('.') + 1:]
        tmp = tempfile.mkdtemp(prefix='vidar-')

        cmd = self._prepare_export_command(fps, format, tmp)
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        input_data = self._export_images(fps)

        stdout, stderr = proc.communicate(input=input_data)

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
