from unittest.mock import Mock, patch

import pytest
from pynput import keyboard

from src.audio_transcriber import AudioTranscriber
from src.cli_interface import CliInterface
from src.whisper_transcription import WhisperTranscription


# Fixture to mock the dependencies of AudioTranscriber
@pytest.fixture
def audio_transcriber_mocked():
    # Mock pyaudio.PyAudio
    pyaudio_mock = Mock()
    pyaudio_instance_mock = Mock()
    pyaudio_mock.PyAudio.return_value = pyaudio_instance_mock

    # Mock WhisperTranscription
    whisper_transcription_mock = Mock(spec=WhisperTranscription)

    # Mock CliInterface.print_welcome
    cli_interface_mock = Mock(spec=CliInterface)
    cli_interface_mock.colorize.return_value = ""

    # Mock setup_audio_device method to return dummy device index and sample rate
    device_index, chosen_sample_rate = 0, 44100

    with patch("src.audio_transcriber.pyaudio", pyaudio_mock), patch(
        "src.audio_transcriber.WhisperTranscription",
        return_value=whisper_transcription_mock,
    ), patch("src.audio_transcriber.CliInterface", cli_interface_mock), patch.object(
        AudioTranscriber,
        "setup_audio_device",
        return_value=(device_index, chosen_sample_rate),
    ):
        # Now when AudioTranscriber is instantiated within this context,
        # it uses the mocked dependencies.
        yield AudioTranscriber("small")


# Test to verify the initial state of AudioTranscriber
def test_audio_transcriber_initialization(audio_transcriber_mocked):
    assert audio_transcriber_mocked.recording is False


# Test to verify the start_recording method
def test_toggle_recording_start(audio_transcriber_mocked):
    audio_transcriber_mocked.start_recording()
    assert audio_transcriber_mocked.recording is True


# Test to verify the pause_recording method
def test_toggle_recording_pause(audio_transcriber_mocked):
    audio_transcriber_mocked.start_recording()
    audio_transcriber_mocked.pause_recording()
    assert audio_transcriber_mocked.recording is False


# Test to verify the on_key_press method for starting recording
def test_on_key_press_toggle_recording(audio_transcriber_mocked):
    key = keyboard.Key.space
    audio_transcriber_mocked.on_key_press(key)
    assert audio_transcriber_mocked.recording is True


# Test to verify the on_key_press method for stopping recording
def test_on_key_press_stop_recording(audio_transcriber_mocked):
    key = keyboard.Key.esc
    audio_transcriber_mocked.recording = True
    audio_transcriber_mocked.on_key_press(key)
    assert audio_transcriber_mocked.recording is False


# Test to verify the on_key_press method for stopping recording and processing
def test_on_key_press_stop_recording_processing(audio_transcriber_mocked):
    key = keyboard.Key.esc
    audio_transcriber_mocked.recording = True
    audio_transcriber_mocked.on_key_press(key)
    assert audio_transcriber_mocked.recording is False


# Test to verify the on_key_press method for stopping recording, processing, and terminating
def test_on_key_press_stop_recording_processing_terminate(audio_transcriber_mocked):
    key = keyboard.Key.esc
    audio_transcriber_mocked.recording = True
    audio_transcriber_mocked.on_key_press(key)
    assert audio_transcriber_mocked.recording is False


# Mock class for keyboard.Listener
class ListenerMock(Mock):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # This method is intentionally left empty.
        pass


# Test to verify the run method of AudioTranscriber
def test_run(audio_transcriber_mocked):
    with patch("src.audio_transcriber.keyboard.Listener", return_value=ListenerMock()) as listener_mock, patch(
        "os.isatty", return_value=False
    ), patch("sys.stdin.fileno"):
        audio_transcriber_mocked.run()
        listener_mock.assert_called_once_with(on_press=audio_transcriber_mocked.on_key_press)
        listener_mock.return_value.join.assert_called_once()
