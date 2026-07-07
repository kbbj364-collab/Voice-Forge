# Voice-Forge

Voice-Forge is a small toolkit providing:

- RVC-based voice cloning (ONNX)
- VITS2 + HiFi-GAN text-to-speech (ONNX)
- Audio utilities for processing and playback

Quick start

1. Install Python deps:

   pip install -r requirements.txt

2. System dependencies (required):

   - espeak-ng (for Bengali TTS fallback)
   - ffmpeg (optional, for conversions)

   On Ubuntu:

   sudo apt-get install espeak-ng ffmpeg

3. Run the CLI demo:

   python -m src.app.cli demo

Synthesize example:

   python -m src.app.cli synthesize -t "Hello world" -o hello.wav

Clone example (saves features as .npy):

   python -m src.app.cli clone -i sample.wav -o cloned_features

Notes

- Models are downloaded and cached by src/engine/models.py on first run.
- ONNX GPU acceleration (CUDA) will be used if available.

