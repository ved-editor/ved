import subprocess
from io import BytesIO
import tempfile
import os
from shutil import rmtree

import pyglet
from pyglet.gl import *  # noqa F403


class Movie:
    """A movie is an instance of ved that acts as a container for layers"""

    def __init__(self, width: int, height: int, nodes=[], background=(0, 0,
    0, 1)):
        self.width = width
        self.height = height
        self.background = background

        self.nodes = nodes
        # Create opengl context (wrapped in an invisible window).
        # This will be used to render the final result.
        self._window = pyglet.window.Window(
            width=width, height=height, visible=False)
        self.current_time = 0.0

    @property
    def duration(self):
        duration = 0.0
        for node in self.nodes:
            duration = max(duration, node.end_time)
        return duration

    def _process_nodes(self):
        for node in self.nodes:
            if node.start_time <= self.current_time < node.end_time:
                node(self)

    def _draw(self):
        glClearColor(*self.background)
        glClear(GL_COLOR_BUFFER_BIT)
        # TODO: draw nodes' outputs

    def tick(self):
        """Call each node"""

        self._process_nodes()
        self._draw()

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
        self.tick()

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
