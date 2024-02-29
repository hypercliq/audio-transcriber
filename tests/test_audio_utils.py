from unittest.mock import Mock

import pytest

from src.audio_utils import (
    choose_audio_device,
    choose_sample_rate,
    find_supported_sample_rates,
    get_audio_devices,
)
from src.config import SAMPLE_RATES


# Fixture to mock supported sample rates
@pytest.fixture
def mock_supported_rates():
    # Return a subset of SAMPLE_RATES for testing
    return [8000, 44100]


# Fixture to mock a PyAudio instance
@pytest.fixture
def mock_pyaudio_instance():
    # Define mock device information
    device_info = [
        {"name": "Device 1", "maxInputChannels": 2},
        {"name": "Device 2", "maxInputChannels": 0},
        {"name": "Device 3", "maxInputChannels": 1},
    ]
    mock_instance = Mock()
    # Set the return value for get_device_count
    mock_instance.get_device_count.return_value = len(device_info)
    # Set the side effect for get_device_info_by_index
    mock_instance.get_device_info_by_index.side_effect = lambda index: device_info[
        index
    ]
    return mock_instance


# Test to verify the get_audio_devices function
def test_get_audio_devices(mock_pyaudio_instance):
    devices = get_audio_devices(mock_pyaudio_instance)
    # Check if the function returns the correct devices
    assert devices == [(0, "Device 1"), (2, "Device 3")]


# Test to verify the choose_audio_device function
def test_choose_audio_device(mocker, mock_pyaudio_instance):
    # Mock user input to select the second device
    mocker.patch("builtins.input", return_value="1")
    device_index = choose_audio_device(mock_pyaudio_instance)
    # Check if the function returns the correct device index
    assert device_index == 1


# Test to verify the find_supported_sample_rates function
def test_find_supported_sample_rates_correctly_filters_rates(
    mock_pyaudio_instance, mock_supported_rates
):
    # Define the side effect for the open method of the PyAudio instance
    def open_side_effect(*args, **kwargs):
        rate = kwargs.get("rate")
        # Raise an exception for unsupported sample rates
        if rate not in mock_supported_rates:
            raise ValueError("Unsupported sample rate")
        else:
            return Mock()  # Simulate a successful stream opening

    mock_pyaudio_instance.open.side_effect = open_side_effect

    # Call the function with the mock PyAudio instance and a device index
    actual_supported_rates = find_supported_sample_rates(mock_pyaudio_instance, 0)
    # Check if the function returns the correct supported sample rates
    assert set(actual_supported_rates) == set(
        mock_supported_rates
    ), "find_supported_sample_rates should return the correct supported rates"


# Test to verify the choose_sample_rate function
def test_choose_sample_rate(mocker):
    # Mock user input to select the second sample rate
    mocker.patch("builtins.input", side_effect=["2"])
    sample_rate = choose_sample_rate([44100, 48000, 96000])
    # Check if the function returns the correct sample rate
    assert sample_rate == 48000
