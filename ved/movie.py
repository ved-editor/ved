import subprocess
from io import BytesIO
import tempfile
import os
from shutil import rmtree
import struct
import wave
from typing import List

import pyglet
from pyglet.gl import *  # noqa F403

from .node.audio import Audio


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
        self._window.switch_to()
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

    def _get_audio_output_nodes(self) -> list:
        def has_audio(node):
            return isinstance(node, Audio) \
                and node.output_audio \
                and node.channels > 0

        return [node for node in self.nodes if has_audio(node)]

    def _write_audio_data(self, node, samples, sample_rate, clip_path):
        f = open(clip_path, 'wb')
        wav = wave.open(f)
        wav.setnchannels(node.channels)
        wav.setframerate(sample_rate)
        wav.setsampwidth(node.sample_size // 8)
        wav.writeframes(samples.getvalue())

    def _prepare_record_command(self, audio_data, frame_rate, sample_rate,
    format, ffmpeg_options, tmp):
        # Since ffmpeg has a hard time with multiple piped inputs, only pipe
        # images and save the audio to temporary files.

        cmd = 'ffmpeg -r {} -f png_pipe -i pipe: '.format(frame_rate)
        audio_id = 0
        for node, samples in audio_data.items():
            clip_path = os.path.join(tmp, 'audio_{}.wav'.format(audio_id))
            self._write_audio_data(node, samples, sample_rate, clip_path)
            cmd += '-itsoffset {} -i {} ' \
                .format(node.start_time, clip_path)
            audio_id += 1

        cmd += '-y -r {} -ar {} -f {} ' \
            .format(frame_rate, sample_rate, format)
        if len(ffmpeg_options) > 0:
            cmd += ' '.join(ffmpeg_options) + ' '
        cmd += 'pipe: -v error'
        return cmd

    def _record_frames(self, start_time, end_time, frame_rate, sample_rate):
        # TODO: add increment argument
        increment = lcm(frame_rate, sample_rate)
        pixel_data = BytesIO()  # concatenation of each frame's pixels
        audio_data = {}  # node: Node -> samples: BytesIO

        self.current_time = start_time
        progress = 0
        while self.current_time <= end_time:
            self.tick()

            # if (seconds since started) % (1 / sample_rate) == 0
            # multiply (seconds since started) and (1 / sample_rate) by
            # increment.
            if progress % (float(increment) / sample_rate) == 0:
                for node in self._get_audio_output_nodes():
                    if node not in audio_data:
                        audio_data[node] = BytesIO()
                    # for each channel
                    for sample in node.samples:
                        if node.sample_size == 8:
                            # Scale float to int
                            i = int(sample * (2 ** 8 - 1))
                            # Pack int to bytes
                            b = struct.pack('<c', bytes([i]))
                        else:
                            # Scale float to int
                            i = int(sample * (2 ** 16 - 1))
                            # Pack int to bytes
                            b = struct.pack('<h', bytes([i]))
                        audio_data[node].write(b)


            # if (seconds since started) % (1 / frame_rate) == 0
            # multiply (seconds since started) and (1 / frame_rate) by
            # increment.
            if progress % (float(increment) / frame_rate) == 0:
                # Save pixels
                # TODO: make sure self._window is the active window
                pyglet.image.get_buffer_manager() \
                    .get_color_buffer() \
                    .get_image_data() \
                    .save(filename='.png', file=pixel_data)
                # TODO: replace .png with an argument

            self.current_time += 1.0 / increment
            # 1 unit of 'progress' is equal to (1 / increment) seconds
            progress += 1

        return pixel_data, audio_data

    def record(self, filename, frame_rate: float, sample_rate: float,
    start_time=0.0, end_time: float = None, file=None,
    ffmpeg_options: List[str] = []):
        """Render the movie from `start_time` to `end_time`"""

        if end_time is None:
            end_time = self.duration

        close_file = False   # close the file when done if we created it here
        if file is None:
            file = open(filename, 'wb')
            close_file = True
        format = filename[filename.rfind('.') + 1:]
        tmp = tempfile.mkdtemp(prefix='ved-')

        pixel_data, audio_data = self._record_frames(start_time, end_time,
            frame_rate, sample_rate)

        cmd = self._prepare_record_command(audio_data, frame_rate,
            sample_rate, format, ffmpeg_options, tmp)
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate(input=pixel_data.getvalue())

        rmtree(tmp)

        if stderr:
            raise RuntimeError('Error running `{}`:\n{}'.format(cmd, stderr))
        file.write(bytes(stdout))
        if close_file:
            file.close()


def gcd(a, b):
    if a == 0:
        return b
    return gcd(b % a, a)


def lcm(a, b):
    return (a * b) / gcd(a, b)
