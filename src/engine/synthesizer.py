#!/usr/bin/env python3
"""
Text-to-Speech synthesis engine supporting multiple languages.
"""

import numpy as np
import librosa
import onnxruntime as ort
from pathlib import Path
import os
import subprocess
import tempfile

from .models import ModelManager
from audio.processor import AudioProcessor


class TextToSpeech:
    """Text-to-Speech synthesis using VITS2 + HiFi-GAN."""

    def __init__(self):
        """Initialize the TTS engine."""
        self.model_manager = ModelManager()
        self.vits_session = None
        self.vocoder_session = None
        self._load_models()

    def _load_models(self):
        """Load ONNX models for TTS and vocoding."""
        # Load VITS2 model
        vits_path = self.model_manager.get_or_download_vits_model()
        self.vits_session = ort.InferenceSession(
            vits_path,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        print(f"✓ Loaded VITS2 model from {vits_path}")
        
        # Load HiFi-GAN vocoder
        vocoder_path = self.model_manager.get_or_download_vocoder_model()
        self.vocoder_session = ort.InferenceSession(
            vocoder_path,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        print(f"✓ Loaded HiFi-GAN vocoder from {vocoder_path}")

    def _text_to_phonemes(self, text: str, language: str) -> np.ndarray:
        """Convert text to phoneme sequence.
        
        Args:
            text: Input text
            language: Language code ('en' or 'bn')
        
        Returns:
            Phoneme sequence as numpy array
        """
        # Simple phoneme conversion (in production, use a proper G2P model)
        phoneme_map = {
            'a': 1, 'e': 2, 'i': 3, 'o': 4, 'u': 5,
            'b': 6, 'c': 7, 'd': 8, 'f': 9, 'g': 10,
            'h': 11, 'k': 12, 'l': 13, 'm': 14, 'n': 15,
            'p': 16, 'r': 17, 's': 18, 't': 19, 'v': 20,
            'w': 21, 'y': 22, 'z': 23, ' ': 0, '.': 24, ',': 25,
        }
        
        text_lower = text.lower()
        phoneme_seq = [phoneme_map.get(c, 0) for c in text_lower]
        return np.array(phoneme_seq, dtype=np.int64)

    def synthesize(self, text: str, language: str = 'English') -> np.ndarray:
        """Synthesize speech from text.
        
        Args:
            text: Input text
            language: Language ('English' or 'Bengali')
        
        Returns:
            Audio samples as numpy array
        """
        if language == 'Bengali':
            return self._synthesize_bengali(text)
        else:
            return self._synthesize_english(text)

    def _synthesize_english(self, text: str) -> np.ndarray:
        """Synthesize English speech using VITS2."""
        # Convert text to phonemes
        phoneme_seq = self._text_to_phonemes(text, 'en')
        phoneme_seq = np.expand_dims(phoneme_seq, 0).astype(np.int64)
        
        # VITS2 inference
        input_name = self.vits_session.get_inputs()[0].name
        output_names = [out.name for out in self.vits_session.get_outputs()]
        
        mel_output = self.vits_session.run(
            output_names,
            {input_name: phoneme_seq}
        )[0]
        
        # Vocoder inference (convert mel-spectrogram to waveform)
        vocoder_input_name = self.vocoder_session.get_inputs()[0].name
        vocoder_output_name = self.vocoder_session.get_outputs()[0].name
        
        waveform = self.vocoder_session.run(
            [vocoder_output_name],
            {vocoder_input_name: mel_output.astype(np.float32)}
        )[0]
        
        return waveform.squeeze().astype(np.float32)

    def _synthesize_bengali(self, text: str) -> np.ndarray:
        """Synthesize Bengali speech using eSpeak-NG."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_file = tmp.name
        
        try:
            # Use espeak-ng for Bengali synthesis
            subprocess.run([
                'espeak-ng',
                '-v', 'bn',  # Bengali voice
                '-w', output_file,
                '-s', '150',  # Speed
                text
            ], check=True, capture_output=True)
            
            # Load generated audio
            audio, sr = librosa.load(output_file, sr=22050)
            return audio.astype(np.float32)
        
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
