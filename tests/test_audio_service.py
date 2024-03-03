from unittest.mock import MagicMock

import pytest
from pynput import keyboard

from src.audio_service import AudioService


# Fixture to mock dependencies and create an instance of AudioService
@pytest.fixture
def audio_service(mocker):
    mocker.patch("src.audio_service.CliInterface.print_welcome")
    mocker.patch("src.audio_service.CliInterface.print_info")
    mocker.patch("src.audio_service.CliInterface.print_exit")

    pyaudio_mock = mocker.patch("src.audio_service.pyaudio.PyAudio")
    audio_device_manager_mock = mocker.patch("src.audio_service.AudioDeviceManager")
    audio_processor_mock = mocker.patch("src.audio_service.AudioProcessor")
    audio_recorder_mock = mocker.patch("src.audio_service.AudioRecorder")

    # Configure the pyaudio_mock to return specific values for get_device_count and get_device_info_by_index
    pyaudio_instance_mock = pyaudio_mock.return_value
    pyaudio_instance_mock.get_device_count.return_value = 2  # Assuming there are 2 devices for the sake of the test
    pyaudio_instance_mock.get_device_info_by_index.return_value = {"maxInputChannels": 1, "name": "Mock Device"}

    service = AudioService()
    service.audio_device_manager = audio_device_manager_mock
    service.audio_processor = audio_processor_mock
    service.audio_recorder = audio_recorder_mock

    return service


def test_on_key_press_stop_recording(audio_service):
    audio_service.audio_recorder.recording = True

    audio_service.on_key_press(keyboard.Key.esc)

    audio_service.audio_recorder.pause_recording.assert_called_with(stop=True)
    audio_service.audio_processor.stop_processing.assert_called_once()
    audio_service.audio_recorder.pyaudio_instance.terminate.assert_called_once()


def test_on_key_press_toggle_recording(audio_service):
    audio_service.audio_recorder.recording = False

    audio_service.on_key_press(keyboard.Key.space)

    audio_service.audio_recorder.toggle_recording.assert_called_once()


def test_on_key_press_no_action(audio_service):
    result = audio_service.on_key_press(keyboard.Key.enter)

    assert result is None


@pytest.mark.parametrize("is_real_file", [True, False])
def test_run_with_real_and_fake_file(audio_service, mocker, is_real_file):
    mock_stdin = mocker.patch("sys.stdin", MagicMock())
    # Ensure fileno() returns an integer. Use 1 for a real file descriptor, -1 or any other non-0 value for fake.
    mock_stdin.fileno.return_value = 1 if is_real_file else -1
    mock_listener = mocker.patch("pynput.keyboard.Listener")

    audio_service.run()

    mock_listener.assert_called_once()
