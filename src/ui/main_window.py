#!/usr/bin/env python3
"""
Main application window using PySimpleGUI.
"""

import PySimpleGUI as sg
import os
from pathlib import Path
import threading
import traceback

from engine.cloner import VoiceCloner
from engine.synthesizer import TextToSpeech
from audio.processor import AudioProcessor
from engine.models import ModelManager


class MainWindow:
    """Main GUI window for Voice Forge application."""

    def __init__(self):
        """Initialize the main window."""
        sg.set_options(
            font=('Segoe UI', 10),
            element_padding=(5, 5),
            margins=(10, 10),
        )
        
        self.cloner = None
        self.tts = None
        self.cloned_voice = None
        self.window = None
        self._init_models()

    def _init_models(self):
        """Initialize models in background thread."""
        def load_models():
            try:
                self.cloner = VoiceCloner()
                self.tts = TextToSpeech()
            except Exception as e:
                print(f"Error loading models: {e}")

        threading.Thread(target=load_models, daemon=True).start()

    def _create_layout(self):
        """Create the GUI layout."""
        layout = [
            # Header
            [
                sg.Text('🎙️ Voice Forge', font=('Segoe UI', 18, 'bold'), text_color='#2E86AB'),
                sg.Push(),
                sg.Button('ℹ️ Help', key='-HELP-', size=(8, 1)),
                sg.Button('⚙️ Settings', key='-SETTINGS-', size=(8, 1)),
            ],
            [sg.HorizontalDivider()],
            
            # Step 1: Voice Cloning
            [
                sg.Text('STEP 1: Clone Your Voice', font=('Segoe UI', 12, 'bold'), text_color='#A23B72'),
            ],
            [
                sg.Text('Upload a voice sample (.wav, .mp3, .flac):'),
            ],
            [
                sg.InputText(
                    key='-VOICE_FILE-',
                    size=(50, 1),
                    disabled=False,
                ),
                sg.FileBrowse(
                    button_text='Browse',
                    file_types=(('Audio Files', '*.wav *.mp3 *.flac'), ('All Files', '*.*')),
                    size=(10, 1),
                ),
            ],
            [
                sg.Button('🔊 Clone Voice', key='-CLONE-', size=(15, 1), button_color=('#FFFFFF', '#2E86AB')),
                sg.Button('Play Sample', key='-PLAY_SAMPLE-', size=(15, 1), disabled=True),
                sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS_CLONE-', visible=False),
            ],
            [sg.Text('Status: Ready', key='-STATUS_CLONE-', text_color='#666')],
            [sg.HorizontalDivider()],
            
            # Step 2: Speech Synthesis
            [
                sg.Text('STEP 2: Generate Speech', font=('Segoe UI', 12, 'bold'), text_color='#A23B72'),
            ],
            [
                sg.Text('Text to synthesize:'),
            ],
            [
                sg.Multiline(
                    size=(60, 6),
                    key='-TEXT_INPUT-',
                    font=('Consolas', 10),
                    background_color='#F5F5F5',
                )
            ],
            [
                sg.Text('Language:'),
                sg.Combo(
                    values=['English', 'Bengali'],
                    default_value='English',
                    key='-LANGUAGE-',
                    size=(15, 1),
                ),
                sg.Text('Voice Quality:'),
                sg.Combo(
                    values=['Fast', 'Balanced', 'High Quality'],
                    default_value='Balanced',
                    key='-QUALITY-',
                    size=(15, 1),
                ),
            ],
            [
                sg.Button('✨ Generate Speech', key='-GENERATE-', size=(20, 1), button_color=('#FFFFFF', '#2E86AB'), disabled=True),
                sg.Button('▶️ Play', key='-PLAY_OUTPUT-', size=(10, 1), disabled=True),
                sg.Button('💾 Export', key='-EXPORT-', size=(10, 1), disabled=True),
            ],
            [sg.Text('Status: Ready', key='-STATUS_SYNTH-', text_color='#666')],
            [sg.ProgressBar(100, orientation='h', size=(60, 20), key='-PROGRESS_SYNTH-', visible=False)],
            [sg.HorizontalDivider()],
            
            # Output log
            [
                sg.Multiline(
                    size=(60, 8),
                    key='-OUTPUT_LOG-',
                    disabled=True,
                    background_color='#1E1E1E',
                    text_color='#00FF00',
                    font=('Consolas', 9),
                )
            ],
            [
                sg.Button('Clear Log', key='-CLEAR_LOG-', size=(10, 1)),
                sg.Push(),
                sg.Button('Exit', key='-EXIT-', size=(10, 1)),
            ],
        ]
        return layout

    def log(self, message):
        """Log a message to the output log."""
        if self.window:
            current = self.window['-OUTPUT_LOG-'].get()
            self.window['-OUTPUT_LOG-'].update(current + message + '\n')
            self.window['-OUTPUT_LOG-'].see()

    def run(self):
        """Run the main event loop."""
        layout = self._create_layout()
        self.window = sg.Window('Voice Forge', layout, finalize=True, size=(700, 900))
        
        self.log('🚀 Voice Forge initialized')
        self.log('Loading models...')
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event in (sg.WINDOW_CLOSED, '-EXIT-'):
                break
            
            if event == '-CLONE-':
                self._on_clone_voice(values['-VOICE_FILE-'])
            
            elif event == '-PLAY_SAMPLE-':
                self._on_play_sample()
            
            elif event == '-GENERATE-':
                self._on_generate_speech(
                    values['-TEXT_INPUT-'],
                    values['-LANGUAGE-'],
                    values['-QUALITY-'],
                )
            
            elif event == '-PLAY_OUTPUT-':
                self._on_play_output()
            
            elif event == '-EXPORT-':
                self._on_export()
            
            elif event == '-CLEAR_LOG-':
                self.window['-OUTPUT_LOG-'].update('')
            
            elif event == '-HELP-':
                self._show_help()
            
            elif event == '-SETTINGS-':
                self._show_settings()
            
            # Check if models are loaded
            if self.cloner and self.tts:
                self.window['-CLONE-'].update(disabled=False)
                self.window['-GENERATE-'].update(disabled=False)
        
        self.window.close()

    def _on_clone_voice(self, voice_file):
        """Handle voice cloning."""
        if not voice_file:
            sg.popup_error('Please select a voice sample file')
            return
        
        if not self.cloner:
            sg.popup_error('Voice cloning model not loaded yet. Please wait...')
            return
        
        try:
            self.log(f'📁 Loading voice sample: {Path(voice_file).name}')
            self.window['-PROGRESS_CLONE-'].update_bar(0)
            self.window['-PROGRESS_CLONE-'].update(visible=True)
            self.window['-STATUS_CLONE-'].update('Status: Processing...')
            self.window.refresh()
            
            # Load and process audio
            audio_data = AudioProcessor.load_audio(voice_file)
            self.log(f'✓ Audio loaded: {len(audio_data)} samples, {len(audio_data) / 22050:.1f}s')
            
            self.window['-PROGRESS_CLONE-'].update_bar(30)
            self.window.refresh()
            
            # Clone voice
            self.cloned_voice = self.cloner.clone(audio_data)
            self.log('✓ Voice cloned successfully!')
            
            self.window['-PROGRESS_CLONE-'].update_bar(100)
            self.window['-STATUS_CLONE-'].update('Status: ✓ Voice cloned', text_color='#00AA00')
            self.window['-PLAY_SAMPLE-'].update(disabled=False)
            self.window['-GENERATE-'].update(disabled=False)
            self.window['-PROGRESS_CLONE-'].update(visible=False)
            
        except Exception as e:
            self.log(f'❌ Error: {str(e)}')
            self.log(traceback.format_exc())
            self.window['-STATUS_CLONE-'].update(f'Status: Error', text_color='#FF0000')
            self.window['-PROGRESS_CLONE-'].update(visible=False)

    def _on_play_sample(self):
        """Play the cloned voice sample."""
        if self.cloned_voice is None:
            sg.popup_error('No voice cloned yet')
            return
        
        try:
            self.log('🔊 Playing voice sample...')
            AudioProcessor.play_audio(self.cloned_voice, 22050)
            self.log('✓ Playback complete')
        except Exception as e:
            self.log(f'❌ Playback error: {str(e)}')

    def _on_generate_speech(self, text, language, quality):
        """Generate speech from text."""
        if not text.strip():
            sg.popup_error('Please enter text to synthesize')
            return
        
        if self.cloned_voice is None:
            sg.popup_error('Please clone a voice first')
            return
        
        if not self.tts:
            sg.popup_error('TTS model not loaded yet')
            return
        
        try:
            self.log(f'🎵 Generating {language} speech...')
            self.window['-PROGRESS_SYNTH-'].update_bar(0)
            self.window['-PROGRESS_SYNTH-'].update(visible=True)
            self.window['-STATUS_SYNTH-'].update('Status: Processing...')
            self.window.refresh()
            
            # Generate speech
            output_audio = self.tts.synthesize(text, language)
            self.log(f'✓ Speech generated: {len(output_audio)} samples')
            
            self.window['-PROGRESS_SYNTH-'].update_bar(100)
            self.window['-STATUS_SYNTH-'].update('Status: ✓ Speech ready', text_color='#00AA00')
            self.window['-PLAY_OUTPUT-'].update(disabled=False)
            self.window['-EXPORT-'].update(disabled=False)
            self.window['-PROGRESS_SYNTH-'].update(visible=False)
            
            self.output_audio = output_audio
            
        except Exception as e:
            self.log(f'❌ Error: {str(e)}')
            self.log(traceback.format_exc())
            self.window['-STATUS_SYNTH-'].update(f'Status: Error', text_color='#FF0000')
            self.window['-PROGRESS_SYNTH-'].update(visible=False)

    def _on_play_output(self):
        """Play generated speech."""
        if not hasattr(self, 'output_audio'):
            sg.popup_error('No speech generated yet')
            return
        
        try:
            self.log('🔊 Playing generated speech...')
            AudioProcessor.play_audio(self.output_audio, 22050)
            self.log('✓ Playback complete')
        except Exception as e:
            self.log(f'❌ Playback error: {str(e)}')

    def _on_export(self):
        """Export generated speech to file."""
        if not hasattr(self, 'output_audio'):
            sg.popup_error('No speech generated yet')
            return
        
        try:
            output_file = sg.save_file(
                'Save audio as',
                default_extension='.wav',
                file_types=(('WAV Files', '*.wav'), ('All Files', '*.*')),
            )
            
            if output_file:
                AudioProcessor.save_audio(self.output_audio, output_file, 22050)
                self.log(f'✓ Audio exported: {Path(output_file).name}')
                sg.popup_ok(f'Audio saved to:\n{output_file}')
        except Exception as e:
            self.log(f'❌ Export error: {str(e)}')

    def _show_help(self):
        """Show help dialog."""
        help_text = '''Voice Forge Help

Step 1: Clone Your Voice
- Select a voice sample (10-30 seconds recommended)
- Click "Clone Voice" to process
- Use "Play Sample" to hear the cloned voice

Step 2: Generate Speech
- Enter text to synthesize
- Choose language and quality
- Click "Generate Speech"
- Play preview or export as WAV

Tips:
- Use clear, consistent voice samples
- Avoid background noise
- English and Bengali fully supported
- All processing happens offline

For more info, visit:
https://github.com/kbbj364-collab/Voice-Forge
        '''
        sg.popup(help_text, title='Voice Forge Help', size=(50, 25))

    def _show_settings(self):
        """Show settings dialog."""
        sg.popup_ok(
            'Settings coming soon!\n\nCurrently supporting:\n- English\n- Bengali\n\nTo clear cached models:\nDelete %APPDATA%\\VoiceForge\\models',
            title='Settings',
        )
