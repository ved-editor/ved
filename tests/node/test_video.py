import pytest   # noqa F401

from ved.node import Video


class TestVideo:
    def test_constructing_1x1_video_does_not_error(self):
        Video(
            start_time=0.0,
            end_time=1.0,
            x=0,
            y=0,
            width=1,
            height=1
        )

    def test_calling_video_node_calls_switch_to(self, mocker):
        node = Video(
            start_time=0.0,
            end_time=1.0,
            x=0,
            y=0,
            width=1,
            height=1
        )
        mocked_switch_to = mocker.patch.object(node.window, 'switch_to')

        node(movie=None)

        mocked_switch_to.assert_called_once()
