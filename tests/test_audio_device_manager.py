import pytest

from src.audio_device_manager import AudioDeviceManager


@pytest.fixture
def audio_device_manager(mocker):
    mock_choose_device = mocker.patch("src.audio_device_manager.choose_audio_device")
    mock_find_rates = mocker.patch("src.audio_device_manager.find_supported_sample_rates")
    mock_choose_rate = mocker.patch("src.audio_device_manager.choose_sample_rate")

    pyaudio_instance = mocker.patch("pyaudio.PyAudio", autospec=True)
    pyaudio_instance.return_value.terminate = mocker.Mock()

    yield AudioDeviceManager(pyaudio_instance), mock_choose_device, mock_find_rates, mock_choose_rate


def test_setup_audio_device_with_supported_rates(audio_device_manager):
    manager, mock_choose_device, mock_find_rates, mock_choose_rate = audio_device_manager
    mock_choose_device.return_value = 0
    mock_find_rates.return_value = [44100]
    mock_choose_rate.return_value = 44100

    device_index, sample_rate = manager.setup_audio_device()

    assert device_index == 0
    assert sample_rate == 44100


def test_setup_audio_device_exits_with_no_supported_rates(mocker, audio_device_manager):
    manager, mock_choose_device, mock_find_rates, mock_choose_rate = audio_device_manager
    mock_choose_device.return_value = 0
    mock_find_rates.return_value = []
    mock_choose_rate.return_value = 44100
    mock_print_error = mocker.patch(
        "src.cli_interface.CliInterface.print_error", return_value="No supported sample rates found for the device."
    )

    with pytest.raises(SystemExit):
        manager.setup_audio_device()

    mock_print_error.assert_called_once_with("No supported sample rates found for the device.")
    manager.pyaudio_instance.terminate.assert_called_once()
