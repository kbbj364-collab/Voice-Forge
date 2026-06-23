#!/usr/bin/env python3
"""
Voice Forge - Desktop Voice Cloning Application
Entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from engine.models import ModelManager


def main():
    """Initialize and run the application."""
    # Ensure model directory exists
    ModelManager.ensure_model_dir()
    
    # Create and run UI
    window = MainWindow()
    window.run()


if __name__ == '__main__':
    main()
