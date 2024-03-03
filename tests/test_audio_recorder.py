import pytest

from src.audio_recorder import AudioRecorder


@pytest.fixture
def mock_dependencies(mocker):
    # Mocking the audio device manager
    audio_device_manager_mock = mocker.patch("src.audio_device_manager.AudioDeviceManager")
    audio_device_manager_mock.setup_audio_device.return_value = (0, 44100)

    pyaudio_instance = mocker.patch("pyaudio.PyAudio", autospec=True)

    # Mocking the audio processor
    audio_processor_mock = mocker.patch("src.audio_processor.AudioProcessor", autospec=True)
    # Simulating that processing is completed
    audio_processor_mock.is_processing_completed.return_value = True

    return audio_device_manager_mock, pyaudio_instance, audio_processor_mock


@pytest.fixture
def audio_recorder(mock_dependencies):
    # Creating an AudioRecorder instance with mocked dependencies
    audio_device_manager_mock, pyaudio_instance, audio_processor_mock = mock_dependencies
    return AudioRecorder(audio_device_manager_mock, pyaudio_instance, audio_processor_mock)


def test_toggle_recording_starts_recording(audio_recorder):
    # Toggling recording should start the recording
    audio_recorder.toggle_recording()
    assert audio_recorder.recording is True
    assert audio_recorder.stream is not None


def test_toggle_recording_pauses_recording(audio_recorder):
    # Toggling recording twice should pause the recording
    audio_recorder.toggle_recording()  # Start recording
    audio_recorder.toggle_recording()  # Pause recording
    assert audio_recorder.recording is False
    assert audio_recorder.stream is None


def test_start_recording_when_already_recording_does_nothing(audio_recorder):
    # Starting recording when already recording should not call pyaudio_instance.open more than once
    audio_recorder.start_recording()
    audio_recorder.start_recording()  # Attempt to start recording again
    audio_recorder.pyaudio_instance.open.assert_called_once()


def test_pause_recording_stops_stream_and_finalizes(audio_recorder):
    # Pausing recording should stop the stream and finalize the recording
    audio_recorder.start_recording()
    audio_recorder.pause_recording(stop=True)
    assert audio_recorder.recording is False
    assert audio_recorder.stream is None
    audio_recorder.audio_processor.finalize_recording.assert_called_once()
    audio_recorder.pyaudio_instance.open().stop_stream.assert_called()
    audio_recorder.pyaudio_instance.open().close.assert_called()


def test_pause_recording_waits_for_processing_completion(audio_recorder):
    # Pausing recording should wait for processing to complete before finalizing
    audio_recorder.start_recording()
    # Simulating that the first call to is_processing_completed returns False, and the second returns True
    audio_recorder.audio_processor.is_processing_completed.side_effect = [False, True]
    audio_recorder.pause_recording(stop=True)
    assert audio_recorder.audio_processor.is_processing_completed.call_count == 2
    assert not audio_recorder.recording, "Recording should be stopped"
    audio_recorder.audio_processor.finalize_recording.assert_called_once()
