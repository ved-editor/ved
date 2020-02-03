import wave
from os.path import join, dirname
import subprocess
from io import BytesIO

import pytest   # noqa F401

from vidar.media import MediaLayer


class TestMedia:
    # Test if the output is a valid wav file. Don't check if it is exactly the
    # same as the input wav file, because it can look different (confirm!).
    def test_wav_audio_data_can_be_read_by_ffprobe(self):
        path = join(dirname(__file__), 'assets', 'audio.wav')
        layer = MediaLayer(path)
        # Write layer audio data to an in-memory wave file
        file = BytesIO()
        wav = wave.open(file, 'wb')
        audio_fmt = layer.audio_format
        wav.setnchannels(audio_fmt.channels)
        wav.setsampwidth(audio_fmt.sample_size // 8)
        wav.setframerate(audio_fmt.sample_rate)
        wav.writeframes(layer.get_audio_data())

        p = subprocess.Popen('ffprobe pipe: -v error', shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=file.getvalue())

        if stderr:
            # only errors are printed, so we know there was an error
            raise RuntimeError(stderr)
        # If there are no errors, pass

    def test_ogv_audio_data_can_be_read_by_ffprobe(self):
        path = join(dirname(__file__), 'assets', 'video.mp4')
        layer = MediaLayer(path)
        # Write layer audio data to an in-memory wave file
        file = BytesIO()
        wav = wave.open(file, 'wb')
        audio_fmt = layer.audio_format
        wav.setnchannels(audio_fmt.channels)
        wav.setsampwidth(audio_fmt.sample_size // 8)
        wav.setframerate(audio_fmt.sample_rate)
        wav.writeframes(layer.get_audio_data())

        p = subprocess.Popen('ffprobe pipe: -v error', shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=file.getvalue())

        if stderr:
            # only errors are printed, so we know there was an error
            raise RuntimeError(stderr)
        # If there are no errors, pass
