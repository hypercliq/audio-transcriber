import os
import sys
import termios
import tty

import pyaudio
from pynput import keyboard

from src.audio_device_manager import AudioDeviceManager
from src.audio_processor import AudioProcessor
from src.audio_recorder import AudioRecorder
from src.cli_interface import CliInterface, start_pause_message


class AudioService:
    def __init__(self):
        CliInterface.print_welcome()
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_device_manager = AudioDeviceManager(self.pyaudio_instance)
        self.audio_processor = AudioProcessor(self.audio_device_manager.chosen_sample_rate)
        self.audio_recorder = AudioRecorder(self.audio_device_manager, self.pyaudio_instance, self.audio_processor)
        CliInterface.print_info(start_pause_message)

    def on_key_press(self, key):
        """
        Handle a key press event. If the space bar is pressed, toggle the recording state.
        If the escape key is pressed, stop recording and processing, terminate the PyAudio instance, and exit the application.
        :param key: The key that was pressed.
        """
        if key == keyboard.Key.space:
            self.audio_recorder.toggle_recording()
        elif key == keyboard.Key.esc:
            if self.audio_recorder.recording:
                self.audio_recorder.pause_recording(stop=True)
            self.audio_processor.stop_processing()
            self.audio_recorder.pyaudio_instance.terminate()
            CliInterface.print_exit()
            return False
        return None

    def run(self):
        """
        Start the main loop of the application. Listens for key press events and handles them with the on_key_press function.
        """
        # Check if sys.stdin is a real file
        if os.isatty(sys.stdin.fileno()):
            # Save the current terminal settings
            old_settings = termios.tcgetattr(sys.stdin)

            try:
                # Disable echoing
                tty.setcbreak(sys.stdin.fileno())

                with keyboard.Listener(on_press=self.on_key_press) as listener:  # type: ignore
                    listener.join()
            finally:
                # Restore the old terminal settings
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        else:
            # sys.stdin is not a real file, so just run the listener
            with keyboard.Listener(on_press=self.on_key_press) as listener:  # type: ignore
                listener.join()
