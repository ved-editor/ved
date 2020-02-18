import io
import os
from os.path import dirname, join

import pytest   # noqa F401
import pyglet
import imageio
import numpy as np

from vidar.movie import Movie
from vidar.layer import Layer
from vidar.media import MediaLayer


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

    def test_render_shows_background_with_no_layers(self):
        PURPLE = (255, 0, 255, 255)
        w = h = 1
        movie = Movie(w, h, background=PURPLE)
        movie._render(0.0)
        expected_data = list(w * h * PURPLE)

        image_data = pyglet.image.get_buffer_manager() \
            .get_color_buffer() \
            .get_image_data()
        actual_data = list(image_data.get_data('RGBA'))

        assert actual_data == expected_data

    def test_process_track_calls_layer_start(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        spy = mocker.spy(layer, 'start')

        movie._process_track(movie.tracks[0], 0.0)

        spy.assert_called_once()

    def test_process_track_calls_layer_stop(self, mocker):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)
        spy = mocker.spy(layer, 'stop')
        track = movie.tracks[0]

        movie._process_track(track, 0.0)
        movie._process_track(track, 2.0)

        spy.assert_called_once()

    def test_export_images_is_not_empty(self):
        movie = Movie(1, 1)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)

        assert len(movie._export_images(10)) > 0

    def test_export_audio_clips_is_correct_size(self):
        movie = Movie(1, 1)
        path = join(dirname(__file__), 'assets', 'audio.wav')
        layer1 = MediaLayer(path)
        layer2 = MediaLayer(path)
        movie.add_layer(0.0, layer1)
        movie.add_layer(0.0, layer2)

        audio_clips = movie._export_audio_clips()

        assert len(audio_clips) == 2

    def test_export_can_save_to_path(self):
        movie = Movie(16, 16)
        layer = Layer(1.0)
        movie.add_layer(0.0, layer)

        movie.export('video.mp4', 24)

        video = imageio.get_reader('video.mp4', format='FFMPEG')

        assert np.array_equal(
            list(video),
            list(np.array([[[[0, 0, 0] for pixel in range(16)]
                for row in range(16)] for frame in range(25)])))
        os.remove(os.path.join(os.getcwd(), 'video.mp4'))

    def test_export_can_save_to_stream(self):
        movie = Movie(16, 16)
        layer = Layer(10.0)
        movie.add_layer(0.0, layer)
        stream = io.BytesIO()

        movie.export('video.mp4', 24)
        movie.export('video.mp4', 24, file=stream)

        stream.seek(0)
        with open('video.mp4', 'rb') as file:
            assert file.read() == stream.read()
        os.remove(os.path.join(os.getcwd(), 'video.mp4'))

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

        movie.screenshot(0.0, filename='screenshot.png', file=stream)
        movie.screenshot(0.0, 'screenshot.png')

        stream.seek(0)
        with open('screenshot.png', 'rb') as file:
            assert file.read() == stream.read()
        os.remove(os.path.join(os.getcwd(), 'screenshot.png'))
