import time

import pyaudio
from pynput import keyboard

from src.audio_utils import (
    choose_audio_device,
    choose_sample_rate,
    find_supported_sample_rates,
)
from src.cli_interface import CliInterface
from src.config import FRAMES_PER_BUFFER
from src.whisper_transcription import WhisperTranscription


class AudioTranscriber:
    def __init__(self, model_size):
        """
        Initialize the AudioTranscriber with the given model size.
        Set up the audio device and transcription service.
        :param model_size: The size of the model to use for transcription.
        """
        self.recording = False
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        self.device_index, self.chosen_sample_rate = self.setup_audio_device()
        self.whisper_transcription = WhisperTranscription(model_size, self.chosen_sample_rate)
        CliInterface.print_welcome()

    def setup_audio_device(self):
        """
        Choose the audio device and sample rate to use for recording.
        :return: The device index and chosen sample rate.
        """
        device_index = choose_audio_device(self.pyaudio_instance)
        supported_rates = find_supported_sample_rates(self.pyaudio_instance, device_index)
        chosen_sample_rate = choose_sample_rate(supported_rates)
        return device_index, chosen_sample_rate

    def toggle_recording(self):
        """
        Toggle the recording state. If currently recording, stop recording.
        If not currently recording, start recording.
        """
        if self.recording:
            self.pause_recording()
            CliInterface.print_recording_paused()
        else:
            self.start_recording()
            CliInterface.print_recording_started()

    def start_recording(self):
        """
        Start recording audio. Opens a new stream with the chosen audio device and sample rate.
        The stream's callback function is set to the transcription service's audio callback function.
        """
        if not self.recording:
            CliInterface.print_initialize_recording()
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.chosen_sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=self.whisper_transcription.audio_callback,
            )
            self.stream.start_stream()
            self.recording = True

    def pause_recording(self, stop=False):
        """
        Pause recording audio. Stop the audio stream and wait for the transcription service to finish processing.
        """
        if self.recording:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            self.whisper_transcription.finalize_recording()
            self.recording = False

        CliInterface.print_recording_pausing(stop)
        while not self.whisper_transcription.is_processing_completed():
            time.sleep(0.1)  # Adjust sleep time as necessary

    def on_key_press(self, key):
        """
        Handle a key press event. If the space bar is pressed, toggle the recording state.
        If the escape key is pressed, stop recording and processing, terminate the PyAudio instance, and exit the application.
        :param key: The key that was pressed.
        """
        if key == keyboard.Key.space:
            self.toggle_recording()
        elif key == keyboard.Key.esc:
            if self.recording:
                self.pause_recording(stop=True)
            self.whisper_transcription.stop_processing()
            self.pyaudio_instance.terminate()
            CliInterface.print_exit()
            return False
        return None

    def run(self):
        """
        Start the main loop of the application. Listens for key press events and handles them with the on_key_press function.
        """
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()
