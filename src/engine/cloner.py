#!/usr/bin/env python3
"""
Voice cloning engine using RVC (Retrieval-based Voice Conversion).
"""

import numpy as np
import librosa
import onnxruntime as ort
from pathlib import Path
import os

from .models import ModelManager
from audio.processor import AudioProcessor


class VoiceCloner:
    """Voice cloning using ONNX-based RVC model."""

    def __init__(self):
        """Initialize the voice cloner."""
        self.model_manager = ModelManager()
        self.session = None
        self.feature_extractor = None
        self._load_model()

    def _load_model(self):
        """Load ONNX model for voice cloning."""
        model_path = self.model_manager.get_or_download_rvc_model()
        
        # Create ONNX session
        self.session = ort.InferenceSession(
            model_path,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        
        print(f"✓ Loaded RVC model from {model_path}")

    def clone(self, audio_data: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Clone voice from audio sample.
        
        Args:
            audio_data: Audio samples (mono or stereo)
            sr: Sample rate (default 22050)
        
        Returns:
            Cloned voice features as numpy array
        """
        # Normalize audio
        audio_data = AudioProcessor.normalize_audio(audio_data, sr)
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = librosa.to_mono(audio_data)
        
        # Ensure float32
        audio_data = audio_data.astype(np.float32)
        
        # Extract features (mel-spectrogram)
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data,
            sr=sr,
            n_fft=2048,
            hop_length=512,
            n_mels=80,
        )
        
        # Convert to log scale
        mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-9)
        
        # Add batch dimension
        mel_spec = np.expand_dims(mel_spec, 0).astype(np.float32)
        
        # Run inference
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        
        cloned_features = self.session.run(
            [output_name],
            {input_name: mel_spec}
        )[0]
        
        return cloned_features.squeeze()
