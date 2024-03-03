from src.audio_utils import (
    choose_audio_device,
    choose_sample_rate,
    find_supported_sample_rates,
)
from src.cli_interface import CliInterface


class AudioDeviceManager:
    def __init__(self, pyaudio_instance):
        self.pyaudio_instance = pyaudio_instance
        self.device_index, self.chosen_sample_rate = self.setup_audio_device()

    def setup_audio_device(self):
        device_index = choose_audio_device(self.pyaudio_instance)
        supported_rates = find_supported_sample_rates(self.pyaudio_instance, device_index)
        if not supported_rates:
            CliInterface.print_error("No supported sample rates found for the device.")
            self.pyaudio_instance.terminate()
            exit(1)
        chosen_sample_rate = choose_sample_rate(supported_rates)
        return device_index, chosen_sample_rate
