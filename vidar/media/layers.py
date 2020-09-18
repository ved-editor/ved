import struct

import pyglet

from ..audio import AudioLayer

# Arbitrary: number of bytes to request at a time.
_BUFFER_SIZE = 1 << 20  # 1 MB


class MediaLayer(AudioLayer):
    def __init__(self, file):
        media = pyglet.media.load(file)
        video_fmt, audio_fmt = media.video_format, media.audio_format
        if audio_fmt:
            super().__init__(media.duration, audio_fmt.channels,
                audio_fmt.sample_size, audio_fmt.sample_rate)
        else:
            super().__init__(media.duration, channels=0, sample_size=None,
                sample_rate=None)
        self.media = media
        self.video_format = VideoFormat(
            video_fmt.width, video_fmt.height, video_fmt.sample_aspect,
            video_fmt.frame_rate) if video_fmt else None
        self.duration = self.media.duration

        if type(file) is str:
            self.file = open(file, 'rb')
        else:
            self.file = file
        self.buffer = None
        self.buffer_pos = 0     # index within buffer
        self._load_sample_buffer()

    def start(self):
        super().start()
        self.media.seek(0.0)

    def sample(self, time):
        # This works with multiple channels, because sample_index
        # alternates between channels.

        if self.buffer is None or self.buffer_pos == _BUFFER_SIZE:
            self._load_sample_buffer()
        # The size of a sample from one channel, in bytes
        sample_size = self.audio_format.sample_size // 8
        data = self.buffer[
            self.buffer_pos:self.buffer_pos + sample_size]
        if len(data) == 0:
            return None
        sample, = struct.unpack('<c' if sample_size == 1 else '<h', data)

        self.buffer_pos += sample_size
        return sample

    def _load_sample_buffer(self):
        packet = self.media.get_audio_data(_BUFFER_SIZE)
        if packet is None:
            raise ValueError('no more audio data left')
        self.buffer = packet.get_string_data()
        self.buffer_pos = 0


# TODO: move to visual module(s) when they are implemented
class VideoFormat:
    def __init__(self, width, height, sample_aspect, frame_rate):
        self.width = width
        self.height = height
        self.sample_aspect = sample_aspect
        self.frame_rate = frame_rate
