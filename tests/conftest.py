import pytest  # noqa F40
import pyglet


@pytest.fixture(scope="function", autouse=True)
def mock_pyglet_window(monkeypatch):
    class MockWindow:
        def __init__(self, width, height, visible):
            pass

    monkeypatch.setattr(pyglet.window, 'Window', MockWindow)
