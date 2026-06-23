# Voice Forge

A modern Windows desktop application that lets anyone clone a voice from a short audio sample and use that voice to generate natural-sounding speech in English and Bengali.

## Features

- **One-Click Voice Cloning**: No terminal, no Python install, no cloud subscription
- **Offline Processing**: All processing happens locally—no cloud calls, no telemetry
- **Multi-Language Support**: English and Bengali with first-class support for additional languages
- **Single Executable**: Standalone `.exe` file that works on any Windows machine
- **Bundled Bengali Font**: Noto Sans Bengali font included for offline rendering
- **Natural-Sounding Speech**: Uses state-of-the-art TTS models (VITS2 + HiFi-GAN)

## System Requirements

- Windows 10 or later (64-bit)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- No Python, Node, or runtime installation required

## Installation

1. Download `VoiceForge.exe` from the [Releases](https://github.com/kbbj364-collab/Voice-Forge/releases) page
2. Double-click to run—no installation needed
3. On first launch, Voice Forge will download required models (~500MB) and store them locally

## Quick Start

1. **Clone a Voice**
   - Click "Upload Voice Sample"
   - Select a `.wav`, `.mp3`, or `.flac` file (10-30 seconds recommended)
   - Click "Clone Voice" and wait for processing

2. **Generate Speech**
   - Type or paste text in the "Text to Synthesize" box
   - Select a language (English or Bengali)
   - Click "Generate Speech"
   - Preview with "Play" or export as `.wav`

## Architecture

- **Voice Cloning**: RVC (Retrieval-based Voice Conversion) via ONNX Runtime
- **Text-to-Speech**: VITS2 + HiFi-GAN for high-quality synthesis
- **UI**: PySimpleGUI for responsive, lightweight interface
- **Packaging**: PyInstaller with single-file output

## Building from Source

### Prerequisites

```bash
python --version  # Python 3.11 or later
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build Executable

```bash
python build/build_exe.py
```

The executable will be created at `dist/VoiceForge.exe`.

### Run Development Version

```bash
python src/app.py
```

## Offline Models

Models are downloaded on first use and cached in:
```
%APPDATA%\VoiceForge\models\
```

Each model is ~200-300MB. Internet connection required for first-time model download only.

## Privacy & Security

- ✅ All processing is local—no data leaves your computer
- ✅ No cloud API calls
- ✅ No telemetry or user tracking
- ✅ Open source—audit the code anytime

## Known Limitations

- English and Bengali only (additional languages coming soon)
- Best results with clear audio samples 10-30 seconds long
- Processing time depends on system specs (typically 10-30 seconds per output)
- Voice cloning works best with consistent speaker tone

## Troubleshooting

### "Models failed to download"
- Check your internet connection
- Ensure you have at least 2GB free disk space
- Try manually clearing `%APPDATA%\VoiceForge\models` and restart

### "Audio file not supported"
- Use `.wav`, `.mp3`, or `.flac` format
- Ensure audio is mono or stereo (not surround)
- Maximum file size: 100MB

### "Speech generation is slow"
- Close other applications to free up RAM
- Reduce text length to test
- Consider upgrading to a machine with an NVIDIA GPU (ONNX Runtime will auto-detect)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

MIT License—see [LICENSE](LICENSE) for details.

## Acknowledgments

- **RVC**: Retrieval-based Voice Conversion by RVC-Project
- **VITS2**: Conditional Variational Autoencoder with Adversarial Learning
- **HiFi-GAN**: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis
- **ONNX Runtime**: Cross-platform inference acceleration by Microsoft
- **eSpeak-NG**: Open-source text-to-speech engine
- **Noto Sans Bengali**: Font by Google

## Support

Issues? Questions?
- Open a [GitHub Issue](https://github.com/kbbj364-collab/Voice-Forge/issues)
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

---

**Made with ❤️ for content creators, podcasters, and accessibility advocates.**
