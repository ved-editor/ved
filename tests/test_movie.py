import io
import subprocess

import pytest   # noqa F401
import imageio
import numpy as np

from ved.movie import Movie
from ved.node import Node
from ved.node.audio import Audio


class TestMovie:
    def test_tick_calls_glClearColor_once(self, mocker):
        # Mock glClearColor in the module where it is used.
        mocked_glClearColor = mocker.patch('ved.movie.glClearColor')
        PURPLE = (255, 0, 255, 255)
        w = h = 1
        movie = Movie(w, h, background=PURPLE)

        movie.tick()

        mocked_glClearColor.assert_called_once_with(*PURPLE)

    def test_tick_switch_to_once(self, mocker):
        # Mock glClearColor in the module where it is used.
        movie = Movie(1, 1)
        mocked_switch_to = mocker.patch.object(movie._window, 'switch_to')

        movie.tick()

        mocked_switch_to.assert_called_once()

    def test_screenshot_can_save_to_stream(self):
        node = Node(0.0, 1.0)
        movie = Movie(1, 1, [node])
        stream = io.BytesIO()

        movie.screenshot(0.0, filename='.png', file=stream)

        stream.seek(0)
        assert np.array_equal(
            imageio.imread(uri=stream, format='png'),
            np.array([[[0, 0, 0, 255]]]))

    def test_play_from_0_to_1_at_framerate_1_calls_tick_twice(self, mocker):
        node = Node(0.0, 1.0)
        movie = Movie(1, 1, [node])
        spy = mocker.spy(movie, 'tick')

        movie.play(0.0, 1.0, 1.0)

        assert spy.call_count == 2

    def test_record_can_save_image_data_to_stream(self):
        node = Node(0.0, 1.0)
        movie = Movie(2, 2, [node])
        stream = io.BytesIO()

        movie.record('.mp4', frame_rate=25, sample_rate=1, file=stream,
            ffmpeg_options=['-movflags frag_keyframe+empty_moov'])

        stream.seek(0)
        video = imageio.get_reader(uri=stream, format='mp4')
        # Every pixel in every frame should be black (0, 0, 0)
        for frame in video:
            for row in frame:
                for pixel in row:
                    assert np.array_equal(np.array([0, 0, 0]), pixel)

    def test_record_can_save_audio_data_to_stream(self, mocker):
        node = Audio(0.0, 1.0, 1, 8, 44100)
        # width needs to be divisible by 2 for ffmpeg
        movie = Movie(2, 2, [node])
        mocked_call = mocker.patch.object(node, '__call__')
        mocked_call.return_value = 0.5
        result = io.BytesIO()

        movie.record('.mp4', frame_rate=1, sample_rate=11025,
            file=result)

        result.seek(0)
        p = subprocess.Popen('ffprobe pipe: -v error', shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=result.getvalue())

        if stderr:
            # only errors are printed, so we know there was an error
            raise AssertionError(stderr)
        # If there are no ffmpeg errors, pass
