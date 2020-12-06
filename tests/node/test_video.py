import pytest   # noqa F401

from ved.node import Video


class TestVideo:
    def test_constructing_1x1_video_does_not_error(self):
        Video(0.0, 1.0, 1, 1)
