from io import BytesIO
import struct
import wave

import pyglet

from ..layer import Layer

# Arbitrary: number of bytes to request at a time.
_BUFFER_SIZE = 1 << 20  # 1 MB


class MediaLayer(Layer):
    def __init__(self, file):
        super().__init__(file)
        self.media = pyglet.media.load(file)
        video_fmt, audio_fmt = self.media.video_format, self.media.audio_format
        self.video_format = VideoFormat(
            video_fmt.width, video_fmt.height, video_fmt.sample_aspect,
            video_fmt.frame_rate) if video_fmt else None
        self.audio_format = AudioFormat(
            audio_fmt.channels, audio_fmt.sample_size,
            audio_fmt.sample_rate) if audio_fmt else None
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

    def get_audio_data(self) -> bytes:
        """Return the bytes for a wave file containing the audio of the layer
        """
        if self.audio_format is None:
            raise ValueError('no audio data available')
        fmt = self.audio_format
        data = BytesIO()
        # Note that there are multiple samples per frame if there is more than
        # one layer
        sample_index = 0
        while True:
            # Calculate time based on sample index
            frame = sample_index // fmt.channels
            time = frame / fmt.sample_rate
            # Allow audio manipulation:
            sample = self.sample(time)
            if sample is None:
                break
            # Now convert the manipulated sample back to bytes
            data.write(struct.pack('<c' if fmt.sample_size == 8 else '<h',
                sample))
            sample_index += 1
        # Convert from sample data to a wav file
        f = BytesIO()
        wav = wave.open(f, 'wb')
        wav.setnchannels(fmt.channels)
        wav.setsampwidth(fmt.sample_size // 8)
        wav.setframerate(fmt.sample_rate)
        wav.writeframes(data.getvalue())
        return f.getvalue()


class VideoFormat:
    def __init__(self, width, height, sample_aspect, frame_rate):
        self.width = width
        self.height = height
        self.sample_aspect = sample_aspect
        self.frame_rate = frame_rate


class AudioFormat:
    def __init__(self, channels, sample_size, sample_rate):
        self.channels = channels
        self.sample_size = sample_size
        self.sample_rate = sample_rate
