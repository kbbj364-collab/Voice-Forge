#!/usr/bin/env python3
"""
Audio processing utilities for loading, saving, and manipulating audio.
"""

import numpy as np
import librosa
import soundfile as sf
import pyaudio
import wave
from typing import Tuple, Optional


class AudioProcessor:
    """Audio processing utilities."""

    SAMPLE_RATE = 22050
    CHUNK_SIZE = 1024

    @staticmethod
    def load_audio(file_path: str, sr: int = 22050) -> np.ndarray:
        """Load audio file.
        
        Args:
            file_path: Path to audio file
            sr: Target sample rate
        
        Returns:
            Audio samples as numpy array
        """
        audio, _ = librosa.load(file_path, sr=sr, mono=True)
        return audio.astype(np.float32)

    @staticmethod
    def save_audio(audio: np.ndarray, file_path: str, sr: int = 22050):
        """Save audio to file.
        
        Args:
            audio: Audio samples
            file_path: Output file path
            sr: Sample rate
        """
        sf.write(file_path, audio, sr, subtype='PCM_16')

    @staticmethod
    def normalize_audio(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Normalize audio to [-1, 1] range.
        
        Args:
            audio: Audio samples
            sr: Sample rate
        
        Returns:
            Normalized audio
        """
        # Remove silence
        S = librosa.feature.melspectrogram(y=audio, sr=sr)
        db = librosa.power_to_db(S, ref=np.max)
        mask = librosa.util.frame(
            db > db.mean() - 20,
            frame_length=2048,
            hop_length=512
        ).any(axis=0)
        
        # Trim silence
        indices = np.where(mask)[0]
        if len(indices) > 0:
            start = indices[0] * 512
            end = (indices[-1] + 1) * 512
            audio = audio[start:end]
        
        # Normalize amplitude
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
        
        return audio

    @staticmethod
    def play_audio(audio: np.ndarray, sr: int = 22050, chunk_size: int = 1024):
        """Play audio using PyAudio.
        
        Args:
            audio: Audio samples
            sr: Sample rate
            chunk_size: Chunk size for playback
        """
        # Ensure audio is in correct format
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sr,
            output=True,
            frames_per_buffer=chunk_size,
        )
        
        try:
            # Play audio in chunks
            for i in range(0, len(audio), chunk_size):
                chunk = audio[i:i + chunk_size]
                stream.write(chunk.tobytes())
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    @staticmethod
    def get_audio_duration(audio: np.ndarray, sr: int = 22050) -> float:
        """Get audio duration in seconds.
        
        Args:
            audio: Audio samples
            sr: Sample rate
        
        Returns:
            Duration in seconds
        """
        return len(audio) / sr

    @staticmethod
    def apply_fade(audio: np.ndarray, fade_in: int = 0, fade_out: int = 0) -> np.ndarray:
        """Apply fade in/out to audio.
        
        Args:
            audio: Audio samples
            fade_in: Fade in duration in samples
            fade_out: Fade out duration in samples
        
        Returns:
            Audio with fade applied
        """
        audio = audio.copy()
        
        if fade_in > 0:
            fade_curve = np.linspace(0, 1, fade_in)
            audio[:fade_in] *= fade_curve
        
        if fade_out > 0:
            fade_curve = np.linspace(1, 0, fade_out)
            audio[-fade_out:] *= fade_curve
        
        return audio

    @staticmethod
    def resample_audio(audio: np.ndarray, sr_orig: int, sr_target: int) -> np.ndarray:
        """Resample audio to target sample rate.
        
        Args:
            audio: Audio samples
            sr_orig: Original sample rate
            sr_target: Target sample rate
        
        Returns:
            Resampled audio
        """
        if sr_orig == sr_target:
            return audio
        
        return librosa.resample(audio, orig_sr=sr_orig, target_sr=sr_target)

    @staticmethod
    def trim_silence(audio: np.ndarray, sr: int = 22050, threshold_db: float = -40) -> np.ndarray:
        """Trim silence from beginning and end of audio.
        
        Args:
            audio: Audio samples
            sr: Sample rate
            threshold_db: Silence threshold in dB
        
        Returns:
            Trimmed audio
        """
        trimmed, _ = librosa.effects.trim(audio, top_db=-threshold_db)
        return trimmed

    @staticmethod
    def mix_audio(audio1: np.ndarray, audio2: np.ndarray, ratio: float = 0.5) -> np.ndarray:
        """Mix two audio signals.
        
        Args:
            audio1: First audio signal
            audio2: Second audio signal
            ratio: Mixing ratio (0-1, where 0 is all audio1, 1 is all audio2)
        
        Returns:
            Mixed audio
        """
        # Ensure same length
        min_len = min(len(audio1), len(audio2))
        audio1 = audio1[:min_len]
        audio2 = audio2[:min_len]
        
        # Mix
        mixed = (1 - ratio) * audio1 + ratio * audio2
        
        # Normalize if clipping
        max_val = np.abs(mixed).max()
        if max_val > 1.0:
            mixed = mixed / max_val
        
        return mixed

    @staticmethod
    def get_amplitude_envelope(audio: np.ndarray, sr: int = 22050, hop_length: int = 512) -> Tuple[np.ndarray, np.ndarray]:
        """Get amplitude envelope of audio.
        
        Args:
            audio: Audio samples
            sr: Sample rate
            hop_length: Hop length for envelope calculation
        
        Returns:
            Tuple of (envelope, times)
        """
        # Calculate RMS energy
        S = librosa.feature.melspectrogram(y=audio, sr=sr)
        energy = librosa.feature.rms(S=S)[0]
        
        # Times
        times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)
        
        return energy, times
