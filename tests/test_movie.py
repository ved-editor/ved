import io
import os
from os.path import dirname, join

import pytest   # noqa F401
import imageio
import numpy as np

from vidar.movie import Movie
from vidar.layer import Layer
from vidar.audio import AudioLayer


class TestMovie:
    def test_add_layer_attaches_layer(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        spy = mocker.spy(layer, 'attach')

        movie.add_layer(0.0, layer)

        spy.assert_called_once_with(movie)

    def test_tracks_append_attaches_layer(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        spy = mocker.spy(layer, 'attach')

        movie.tracks.append((0.0, layer))

        spy.assert_called_once_with(movie)

    def test_remove_layer_detaches_layer(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        spy = mocker.spy(layer, 'detach')

        movie.remove_layer(layer)

        spy.assert_called_once()

    def test_tracks_filter_detaches_layer(self, mocker):
        movie = Movie(1, 1)
        test_layer = Layer(1.0)
        movie.add_layer(0.0, test_layer)
        spy = mocker.spy(test_layer, 'detach')

        movie.tracks = [(time, layer) for time, layer in movie.tracks
            if layer != test_layer]

        spy.assert_called_once()

    def test_screenshot_without_any_layers_calls_glClearColor_once(self, mocker):
        # mock where it's used
        mocked_glClearColor = mocker.patch('vidar.movie.glClearColor')
        PURPLE = (255, 0, 255, 255)
        w = h = 1
        movie = Movie(w, h, background=PURPLE)

        movie.screenshot(0.0, '.png', io.BytesIO())

        mocked_glClearColor.assert_called_once_with(*PURPLE)

    def test_screenshot_calls_layer_start(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        spy = mocker.spy(layer, 'start')

        movie.screenshot(0.0, '.png', io.BytesIO())

        spy.assert_called_once()

    def test_screenshots_calls_layer_stop(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        spy = mocker.spy(layer, 'stop')

        # start
        movie.screenshot(0.0, '.png', io.BytesIO())
        # stop
        movie.screenshot(2.0, '.png', io.BytesIO())

        spy.assert_called_once()

    def test_screenshot_can_save_to_path(self):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)

        movie.screenshot(0.0, 'screenshot.png')

        assert np.array_equal(
            imageio.imread('screenshot.png'),
            np.array([[[0, 0, 0, 255]]]))
        os.remove(os.path.join(os.getcwd(), 'screenshot.png'))

    def test_screenshot_can_save_to_stream(self):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        stream = io.BytesIO()

        movie.screenshot(0.0, filename='.png', file=stream)

        stream.seek(0)
        assert np.array_equal(
            imageio.imread(uri=stream, format='png'),
            np.array([[[0, 0, 0, 255]]]))

    def test_export_can_save_image_data_to_path(self):
        movie = Movie(16, 16)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)

        movie.export('video.mp4', 24)

        video = imageio.get_reader('video.mp4', format='FFMPEG')
        for frame in video:
            for row in frame:
                for pixel in row:
                    assert np.array_equal(np.array([0, 0, 0]), pixel)
        os.remove(os.path.join(os.getcwd(), 'video.mp4'))

    def test_export_can_save_image_data_to_stream(self):
        movie = Movie(16, 16)
        layer = Layer(10.0)
        movie.add_layer(0.0, layer)
        stream = io.BytesIO()

        movie.export('.mp4', 24, file=stream)

        stream.seek(0)
        video = imageio.get_reader(uri=stream, format='mp4')
        for frame in video:
            for row in frame:
                for pixel in row:
                    assert np.array_equal(np.array([0, 0, 0]), pixel)

    def test_export_can_save_audio_data_to_path(self, mocker):
        movie = Movie(2, 2) # width needs to be divisible by 2 for ffmpeg
        layer = AudioLayer(1.0, 1, None, None)
        # get_audio_data returns the audio data in wav format, so we can mock
        # that to return the contents of a real wav file.
        mocked_get_audio_data = mocker.patch.object(layer, 'get_audio_data')
        with open(join(dirname(__file__), 'assets', 'audio.wav'), 'rb') as audio:
            mocked_get_audio_data.return_value = audio.read()
        movie.add_layer(0.0, layer)

        movie.export('video.mp4', 24)

        with open('video.mp4', 'rb') as result:
            p = subprocess.Popen('ffprobe pipe: -v error', shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = p.communicate(input=result.read())

            if stderr:
                # only errors are printed, so we know there was an error
                raise AssertionError(stderr)
        # If there are no ffmpeg errors, pass
        os.remove(os.path.join(os.getcwd(), 'video.mp4'))

    def test_export_can_save_audio_data_to_stream(self, mocker):
        movie = Movie(2, 2) # width needs to be divisible by 2 for ffmpeg
        layer = AudioLayer(1.0, 1, None, None)
        # get_audio_data returns the audio data in wav format, so we can mock
        # that to return the contents of a real wav file.
        mocked_get_audio_data = mocker.patch.object(layer, 'get_audio_data')
        with open(join(dirname(__file__), 'assets', 'audio.wav'), 'rb') as audio:
            mocked_get_audio_data.return_value = audio.read()
        movie.add_layer(0.0, layer)
        result = io.BytesIO()

        movie.export('.mp4', 24, file=result)

        result.seek(0)
        p = subprocess.Popen('ffprobe pipe: -v error', shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=result.getvalue())

        if stderr:
            # only errors are printed, so we know there was an error
            raise AssertionError(stderr)
        # If there are no ffmpeg errors, pass
