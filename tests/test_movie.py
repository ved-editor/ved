import io
import subprocess
import struct

from pyglet import shapes
import pytest   # noqa F401
import imageio
import numpy as np
import wave

from ved.movie import Movie
from ved.node import Node
from ved.node.video import Video
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

    def test_screenshot_can_save_image_data_to_stream_with_a_video_node(self):
        node = Video(0.0, 1.0, x=0, y=0, width=1, height=1)
        # Render a blue pixel over the video node
        node.window.switch_to()
        rect = shapes.Rectangle(x=0, y=0, width=1, height=1, color=(0, 0, 255))
        rect.draw()

        movie = Movie(2, 2, [node])
        stream = io.BytesIO()

        movie.screenshot(0.0, '.png', file=stream)

        stream.seek(0)
        frame = imageio.imread(uri=stream, format='png')
        expected_frame = np.array([
            [[0, 0, 0, 255], [0, 0, 0, 255]],
            [[0, 0, 0, 255], [0, 0, 255, 255]]
        ])
        assert np.array_equal(expected_frame, frame)

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
        node = Audio(0.0, 0.01, 1, 8)
        node.samples = 0.5,  # constant sample output (won't be overwritten)
        # width needs to be divisible by 2 for ffmpeg
        movie = Movie(2, 2, [node])
        result = io.BytesIO()

        # .avi files can copy the streams from the (lossness) wav files that
        # are created by ved, so no data is lost.
        movie.record('.avi', frame_rate=1, sample_rate=11025,
            file=result, ffmpeg_options=['-c:a copy'])

        result.seek(0)
        p = subprocess.Popen('ffmpeg -f avi -i pipe: -f wav pipe: -v error',
            shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=result.getvalue())

        if stderr:
            # '-v error' is set, so we know there was an error if stderr is
            # nonempty.
            raise AssertionError(stderr)

        f = io.BytesIO(stdout)
        wav = wave.open(f, 'rb')
        n = wav.getnframes()
        w = wav.getsampwidth()

        # There should only be 1 audio channel, but the sample width may not be
        # 1 byte. For now, this is acceptable, but TODO: investigate this.
        def unpack_to_float(frame):
            # if the sample width is 2, interpret bytes as a short
            # if the sample width is 1, interpret them as a character
            format_ = '<h' if w == 2 else '<b'
            i = int(struct.unpack(format_, frame)[0])  # unpack bytes to int
            # Subtract one because [-1, 1] spans 2 units already.
            exp = 8 * w - 1
            return i / (2.0 ** exp)  # scale int to float

        # Read actual frames
        frames = wav.readframes(n)
        samples = []
        for i in range(0, len(frames), w):
            samples.append(unpack_to_float(frames[i:i + w]))

        # Comapre with expected frames
        expected_n = int(0.01 * 11025 + 1)  # + 1 for last frame
        assert samples == [0.5] * expected_n
