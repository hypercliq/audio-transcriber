import pyaudio

from config import SAMPLE_RATES


def list_audio_devices(pyaudio_instance):
    """
    Lists available audio devices.
    :param pyaudio_instance: An instance of PyAudio.
    """
    print("Available audio devices:")
    info = pyaudio_instance.get_host_api_info_by_index(0)
    num_devices = info.get("deviceCount")
    for i in range(0, num_devices):
        if pyaudio_instance.get_device_info_by_index(i).get("maxInputChannels") > 0:
            device_name = pyaudio_instance.get_device_info_by_index(i).get("name")
            print(f"{i}: {device_name}")


def choose_audio_device(pyaudio_instance):
    """
    Allows the user to choose an audio device by index.
    :param pyaudio_instance: An instance of PyAudio.
    :return: The index of the chosen audio device.
    """
    list_audio_devices(pyaudio_instance)
    device_index = int(input("Enter the index of the desired audio device: "))
    return device_index


def find_supported_sample_rates(pyaudio_instance, device_index):
    """
    Tests and returns a list of supported sample rates for the chosen device.
    :param pyaudio_instance: An instance of PyAudio.
    :param device_index: The index of the chosen audio device.
    :return: A list of supported sample rates.
    """
    sample_rates = SAMPLE_RATES
    supported_rates = []
    print("Testing supported sample rates for the device:")
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
            print(f"Supported: {rate} Hz")
        except Exception:
            continue
    return supported_rates


def choose_sample_rate(supported_rates):
    """
    Allows the user to choose a sample rate from a list of supported rates.
    :param supported_rates: A list of supported sample rates.
    :return: The chosen sample rate.
    """
    print("Supported sample rates: ", supported_rates)
    rate = int(input("Enter the desired sample rate from the list above: "))
    if rate in supported_rates:
        return rate
    else:
        print("Invalid selection. Please choose a rate from the list.")
        return choose_sample_rate(supported_rates)
