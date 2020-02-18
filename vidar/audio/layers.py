from io import BytesIO
import struct
import wave

from ..layer import Layer

# Arbitrary: number of bytes to request at a time.
_BUFFER_SIZE = 1 << 20  # 1 MB


class AudioLayer(Layer):
    def __init__(self, duration):
        super().__init__(duration)

    def sample(self, time):
        """Sample the next frame"""
        return 0.0  # silence

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
