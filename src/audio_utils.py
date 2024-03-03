import pyaudio

from src.cli_interface import CliInterface
from src.config import SAMPLE_RATES


def get_audio_devices(pyaudio_instance):
    """
    Lists the available audio devices.
    :param pyaudio_instance: An instance of the PyAudio class.
    """
    return [
        (i, pyaudio_instance.get_device_info_by_index(i).get("name"))
        for i in range(pyaudio_instance.get_device_count())
        if pyaudio_instance.get_device_info_by_index(i).get("maxInputChannels") > 0
    ]


def choose_audio_device(pyaudio_instance):
    """
    Prompts the user to choose an audio device from the list of available devices.
    :param pyaudio_instance: An instance of the PyAudio class.
    :return: The index of the chosen audio device.
    """
    devices = get_audio_devices(pyaudio_instance)
    CliInterface.print_info("Available audio devices:\n")
    for i, name in enumerate(devices, start=1):
        print(CliInterface.colorize(f"{i})", bold=True) + f" {name[1]}")
    choice = int(input("\n" + CliInterface.format_question("Enter the number corresponding to the desired device: ")))
    return devices[choice - 1][0]


def find_supported_sample_rates(pyaudio_instance, device_index):
    """
    Finds the sample rates supported by the chosen audio device.
    :param pyaudio_instance: An instance of the PyAudio class.
    :param device_index: The index of the chosen audio device.
    :return: A list of supported sample rates.
    """
    sample_rates = SAMPLE_RATES
    supported_rates = []
    for rate in sample_rates:
        try:
            stream = pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=4096,
            )
            stream.close()
            supported_rates.append(rate)
        except Exception:
            continue
    CliInterface.print_info("Supported sample rates for the device:")
    for rate in supported_rates:
        CliInterface.print_success(f"Supported: {rate} Hz")
    return supported_rates


def choose_sample_rate(supported_rates):
    """
    Prompts the user to choose a sample rate from the list of supported rates.
    :param supported_rates: A list of supported sample rates.
    :return: The chosen sample rate.
    """
    CliInterface.print_info("Choose a sample rate for recording:\n")
    for i, rate in enumerate(supported_rates, start=1):
        print(f"{i}) {rate} Hz")
    try:
        choice = int(input("\n" + CliInterface.format_question("Enter the number corresponding to the desired sample rate: ")))
        if 1 <= choice <= len(supported_rates):
            return supported_rates[choice - 1]
        else:
            CliInterface.print_warning("Invalid selection. Please enter a number from the list.")
            return choose_sample_rate(supported_rates)
    except ValueError as e:
        CliInterface.print_error(e)
        return choose_sample_rate(supported_rates)
