import time

import pyaudio

from src.cli_interface import CliInterface, start_pause_message
from src.config import FRAMES_PER_BUFFER


class AudioRecorder:
    def __init__(self, audio_device_manager, pyaudio_instance, audio_processor):
        self.audio_device_manager = audio_device_manager
        self.pyaudio_instance = pyaudio_instance
        self.audio_processor = audio_processor
        self.recording = False
        self.stream = None

    def toggle_recording(self):
        """
        Toggle the recording state.
        If the application is currently recording, it will be paused.
        If the application is currently paused, it will start recording.
        """
        if self.recording:
            self.pause_recording()
            print(CliInterface.colorize("\r\n\u23f8", bold=True) + " Recording paused. " + start_pause_message)
        else:
            self.start_recording()
            print(CliInterface.colorize("\r\n\u25cf", red=True) + " Recording started. " + start_pause_message)

    def start_recording(self):
        """
        Start recording audio. Opens a new stream with the chosen audio device and sample rate.
        The stream's callback function is set to the transcription service's audio callback function.
        """
        if not self.recording:
            CliInterface.print_info("Initializing recording...")
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.audio_device_manager.chosen_sample_rate,
                input=True,
                input_device_index=self.audio_device_manager.device_index,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=self.audio_processor.audio_callback,
            )
            self.stream.start_stream()
            self.recording = True

    def pause_recording(self, stop=False):
        """
        Pause recording audio. Stop the audio stream and wait for the transcription service to finish processing.
        If stop is True, it indicates that the recording is being stopped, not just paused.

        :param stop: Whether the recording is being stopped.
        """
        CliInterface.print_info(
            "Pausing recording... wait for processing to complete"
            if not stop
            else "Stopping recording... wait for processing to complete"
        )

        if self.recording:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            self.audio_processor.finalize_recording()
            self.recording = False

        while not self.audio_processor.is_processing_completed():
            time.sleep(0.1)  # Adjust sleep time as necessary
