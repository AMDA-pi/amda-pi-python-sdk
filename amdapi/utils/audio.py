"""Helper Functions for dealing with Audio data."""

import io
from io import BufferedReader
from typing import Any, Dict, Tuple

from pydub import AudioSegment


def is_stereo(audio: AudioSegment) -> bool:
    """Determines if the audio is stereo.

    Args:
        audio (AudioSegment): PyDub AudioSegment

    Returns:
        bool: Will return True if audio is stereo.
    """
    return audio.channels == 2


def get_metrics(audio: AudioSegment) -> Dict[str, Any]:
    """Returns meta-data of audio. (Bitrate/SampleRate etc)

    Args:
        audio (AudioSegment): PyDub AudioSegment

    Returns:
        Dict[str, Any]: Returns a dictionary containing audio meta-data.
    """
    bitrate = audio.frame_rate * audio.channels * audio.sample_width * 8
    metrics = {
        "sample_rate": audio.frame_rate,
        "bit_depth": audio.sample_width * 8,
        "channels": audio.channels,
        "bitrate": bitrate,
        "file_size": bitrate * len(audio) / (1_000_000_000 * 8),
    }
    return metrics


def get_audio_objects(audio_buffer: BufferedReader) -> Tuple[bytes, AudioSegment]:
    """Reads the audio data into memory, and prepares an audio object for further logic.

    Args:
        audio (BufferedReader): Buffer containing audio data.

    Returns:
        Tuple[bytes, AudioSegment]: (Byte Representation of Audio, AudioSegment Object for Logic)
    """

    audio_bytes = audio_buffer.read()
    audio_object = AudioSegment.from_wav(io.BytesIO(audio_bytes))
    return audio_bytes, audio_object
