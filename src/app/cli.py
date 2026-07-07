#!/usr/bin/env python3
"""
Simple command-line interface for Voice-Forge: TTS and voice cloning demo.
"""

import argparse
import sys
from pathlib import Path

from engine.synthesizer import TextToSpeech
from engine.cloner import VoiceCloner
from audio.processor import AudioProcessor


def synthesize(args):
    tts = TextToSpeech()
    print(f"Synthesizing text ({args.language}): {args.text}")
    waveform = tts.synthesize(args.text, language=args.language)
    out_path = Path(args.output)
    AudioProcessor.save_audio(waveform, str(out_path), sr=22050)
    dur = AudioProcessor.get_audio_duration(waveform, sr=22050)
    print(f"Saved TTS audio to {out_path} ({dur:.2f}s)")


def clone(args):
    cloner = VoiceCloner()
    audio = AudioProcessor.load_audio(args.input, sr=22050)
    print(f"Running voice cloning on {args.input}...")
    features = cloner.clone(audio, sr=22050)
    out_path = Path(args.output)
    # Save features as numpy array
    import numpy as _np
    _np.save(out_path, features)
    print(f"Saved cloned features to {out_path}.npy (shape={features.shape})")


def demo(args):
    """Run a short end-to-end demo: synthesize and play."""
    tts = TextToSpeech()
    text = args.text or "Hello from Voice-Forge"
    print(f"Demo synth: {text}")
    waveform = tts.synthesize(text, language=args.language)
    print("Playing audio...")
    AudioProcessor.play_audio(waveform, sr=22050)


def main():
    parser = argparse.ArgumentParser(prog="voiceforge", description="Voice-Forge CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_syn = sub.add_parser("synthesize", help="Synthesize text to speech")
    p_syn.add_argument("-t", "--text", required=True, help="Text to synthesize")
    p_syn.add_argument("-l", "--language", default="English", choices=["English", "Bengali"], help="Language")
    p_syn.add_argument("-o", "--output", default="out_tts.wav", help="Output WAV path")
    p_syn.set_defaults(func=synthesize)

    p_cl = sub.add_parser("clone", help="Run voice cloning on an input audio file and save features")
    p_cl.add_argument("-i", "--input", required=True, help="Input audio file (sample for cloning)")
    p_cl.add_argument("-o", "--output", default="cloned_features", help="Output .npy path prefix")
    p_cl.set_defaults(func=clone)

    p_demo = sub.add_parser("demo", help="Run a short demo (synthesize + play)")
    p_demo.add_argument("-t", "--text", default="Hello from Voice-Forge", help="Demo text")
    p_demo.add_argument("-l", "--language", default="English", choices=["English", "Bengali"], help="Language")
    p_demo.set_defaults(func=demo)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
