import pyaudio
from pynput import keyboard

from audio_utils import (
    choose_audio_device,
    choose_sample_rate,
    find_supported_sample_rates,
)
from config import FRAMES_PER_BUFFER
from whisper_transcription import WhisperTranscription


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
        self.whisper_transcription = WhisperTranscription(
            model_size, self.chosen_sample_rate
        )

    def setup_audio_device(self):
        """
        Choose the audio device and sample rate to use for recording.
        :return: The device index and chosen sample rate.
        """
        device_index = choose_audio_device(self.pyaudio_instance)
        supported_rates = find_supported_sample_rates(
            self.pyaudio_instance, device_index
        )
        chosen_sample_rate = choose_sample_rate(supported_rates)
        return device_index, chosen_sample_rate

    def toggle_recording(self):
        """
        Toggle the recording state. If currently recording, stop recording.
        If not currently recording, start recording.
        """
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """
        Start recording audio. Opens a new stream with the chosen audio device and sample rate.
        The stream's callback function is set to the transcription service's audio callback function.
        """
        if(not self.recording):
          print("Preparing to start recording...")
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
          print("Recording started. Press Space to stop.")
          self.recording = True

    def stop_recording(self):
        """
        Stop recording audio. Closes the current stream and finalizes the recording in the transcription service.
        """
        if(self.recording):
          print("Stopping recording...")
          if self.stream:
              self.stream.stop_stream()
              self.stream.close()
              self.stream = None
          self.whisper_transcription.finalize_recording()
          print("done")
          self.recording = False

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
                self.stop_recording()
            self.whisper_transcription.stop_processing()
            self.pyaudio_instance.terminate()
            print("Exiting application...")
            return False

    def run(self):
        """
        Start the main loop of the application. Listens for key press events and handles them with the on_key_press function.
        """
        print("Press Space to start/stop recording, Esc to exit.")
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()
