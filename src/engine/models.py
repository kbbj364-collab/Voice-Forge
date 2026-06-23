#!/usr/bin/env python3
"""
Model management: downloading and caching ML models.
"""

import os
import urllib.request
from pathlib import Path
import hashlib
import json


class ModelManager:
    """Manage downloading and caching of ML models."""

    # Model URLs (using public/self-hosted models)
    MODEL_URLS = {
        'rvc': 'https://huggingface.co/spaces/innnky/RVC/resolve/main/weights/model.onnx',
        'vits2': 'https://huggingface.co/espeak-ng-data/vits2/resolve/main/model.onnx',
        'vocoder': 'https://huggingface.co/rinna/japanese-gpt2-medium/resolve/main/vocoder.onnx',
    }

    def __init__(self):
        """Initialize model manager."""
        self.model_dir = self._get_model_dir()

    @staticmethod
    def _get_model_dir() -> Path:
        """Get model cache directory."""
        if os.name == 'nt':  # Windows
            model_dir = Path(os.environ.get('APPDATA', '.')) / 'VoiceForge' / 'models'
        else:  # Linux/Mac
            model_dir = Path.home() / '.cache' / 'voiceforge' / 'models'
        
        model_dir.mkdir(parents=True, exist_ok=True)
        return model_dir

    @staticmethod
    def ensure_model_dir():
        """Ensure model directory exists."""
        ModelManager._get_model_dir()

    def _get_model_path(self, model_name: str) -> Path:
        """Get local path for a model."""
        return self.model_dir / f"{model_name}.onnx"

    def _download_model(self, model_name: str, url: str):
        """Download a model from URL with progress tracking."""
        local_path = self._get_model_path(model_name)
        
        if local_path.exists():
            print(f"✓ Model {model_name} already cached")
            return local_path
        
        print(f"📥 Downloading {model_name}...")
        
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, int(downloaded * 100 / total_size))
            print(f"  Progress: {percent}%", end='\r')
        
        try:
            urllib.request.urlretrieve(url, local_path, download_progress)
            print(f"\n✓ Downloaded {model_name}")
            return local_path
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            raise

    def get_or_download_rvc_model(self) -> Path:
        """Get RVC voice conversion model."""
        model_name = 'rvc'
        url = self.MODEL_URLS.get(model_name)
        if not url:
            raise ValueError(f"No URL for model {model_name}")
        
        return self._download_model(model_name, url)

    def get_or_download_vits_model(self) -> Path:
        """Get VITS2 text-to-speech model."""
        model_name = 'vits2'
        url = self.MODEL_URLS.get(model_name)
        if not url:
            raise ValueError(f"No URL for model {model_name}")
        
        return self._download_model(model_name, url)

    def get_or_download_vocoder_model(self) -> Path:
        """Get HiFi-GAN vocoder model."""
        model_name = 'vocoder'
        url = self.MODEL_URLS.get(model_name)
        if not url:
            raise ValueError(f"No URL for model {model_name}")
        
        return self._download_model(model_name, url)

    def clear_cache(self):
        """Clear model cache."""
        import shutil
        if self.model_dir.exists():
            shutil.rmtree(self.model_dir)
            print(f"✓ Cleared model cache: {self.model_dir}")

    def get_cache_info(self) -> dict:
        """Get cache information."""
        info = {
            'cache_dir': str(self.model_dir),
            'models': {},
            'total_size': 0,
        }
        
        for model_file in self.model_dir.glob('*.onnx'):
            size = model_file.stat().st_size
            info['models'][model_file.stem] = {
                'path': str(model_file),
                'size_mb': size / (1024 ** 2),
            }
            info['total_size'] += size
        
        info['total_size_mb'] = info['total_size'] / (1024 ** 2)
        return info
