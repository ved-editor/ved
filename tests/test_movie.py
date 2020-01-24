import pytest   # noqa F401

from vidar.movie import Movie
from vidar.layer import Layer


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

        spy.assert_called_once_with()

    def test_tracks_filter_detaches_layer(self, mocker):
        movie = Movie(1, 1)
        test_layer = Layer(1.0)
        movie.add_layer(0.0, test_layer)
        spy = mocker.spy(test_layer, 'detach')

        movie.tracks = [(time, layer) for time, layer in movie.tracks
            if layer != test_layer]

        spy.assert_called_once_with()
