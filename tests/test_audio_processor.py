import pytest

from src.audio_processor import AudioProcessor

MOCK_FILE_PATH = "/tmp/mockfile.wav"


# Use a fixture to create a test instance of AudioProcessor
@pytest.fixture
def audio_processor(mocker):
    mocker.patch("src.whisper_service.WhisperService")
    mocker.patch("src.cli_interface.CliInterface")
    mocker.patch("tempfile.mkstemp", return_value=(None, MOCK_FILE_PATH))
    mocker.patch("wave.open", autospec=True)
    mocker.patch("os.close")

    processor = AudioProcessor(chosen_sample_rate=16000)
    yield processor  # This yields control back to the test function

    # Teardown logic to ensure the thread is stopped
    processor.is_processing = False
    processor.processing_thread.join()


def test_process_audio_chunk_volume(audio_processor):
    # Test volume calculation with mock data
    mock_data = b"\x00\x01" * 100  # Mock audio data
    volume = audio_processor.process_audio_chunk_volume(mock_data)
    assert volume != -float("inf"), "Volume should be calculable and not -inf"


def test_audio_callback_adds_data_to_buffer(audio_processor):
    # Test that audio_callback adds data to the buffer correctly
    mock_data = b"\x00\x01" * 1000  # Mock audio data
    audio_processor.audio_callback(in_data=mock_data, _frame_count=None, _time_info=None, _status=None)
    assert len(audio_processor.audio_buffer) == len(mock_data), "Buffer should contain the mock data"


def test_finalize_recording_processes_remaining_data(audio_processor, mocker):
    # Mock the method that will be called when finalizing recording to verify it's called correctly
    process_and_queue_chunk_mock = mocker.patch.object(audio_processor, "process_and_queue_chunk")

    # Simulate remaining data in the buffer
    audio_processor.audio_buffer = b"\x00\x01" * 100
    audio_processor.finalize_recording()

    # Verify the process_and_queue_chunk method was called
    process_and_queue_chunk_mock.assert_called_once()


def test_stop_processing_thread(audio_processor, mocker):
    # Mock the join method to ensure it's called, indicating the thread is waited on to finish
    join_mock = mocker.patch.object(audio_processor.processing_thread, "join")

    audio_processor.stop_processing()

    # Check that is_processing is False and join has been called, ensuring thread termination
    assert not audio_processor.is_processing, "Processing should be stopped"
    join_mock.assert_called_once()


def test_integration_with_whisper_service(audio_processor, mocker):
    # Ensure is_processing is True to start processing
    audio_processor.is_processing = True

    # Mock the transcribe_audio_chunk method of WhisperService
    transcribe_mock = mocker.patch.object(audio_processor.whisper_transcription, "transcribe_audio_chunk")

    # Simulate processing an audio chunk
    mock_data = b"\x00\x01" * 1000  # Mock audio data
    temp_file_path = MOCK_FILE_PATH  # Assuming tempfile.mkstemp is mocked to return this path
    volume_db = audio_processor.process_audio_chunk_volume(mock_data)
    audio_processor.processing_queue.put((mock_data, temp_file_path, volume_db))

    # Adjust is_processing to False to allow the processing loop to exit
    audio_processor.is_processing = False
    audio_processor.process_audio_chunks_queue()  # Process the queue item

    # Verify WhisperService.transcribe_audio_chunk is called correctly
    transcribe_mock.assert_called_once_with(temp_file_path, volume_db)


def test_silent_audio_volume_calculation(audio_processor):
    # Silent audio data
    silent_data = b"\x00\x00" * 1000
    volume = audio_processor.process_audio_chunk_volume(silent_data)
    assert volume == -float("inf"), "Volume of silent audio should be -inf"


def test_process_and_queue_chunk(audio_processor, mocker):
    # Mock the tempfile and wave.open to avoid actual file operations
    mkstemp_mock = mocker.patch("tempfile.mkstemp", return_value=(None, MOCK_FILE_PATH))
    wave_open_mock = mocker.patch("wave.open")

    # Simulate adding data to the buffer and processing it
    mock_data = b"\x00\x01" * 1000  # Enough data to trigger processing
    audio_processor.audio_buffer = mock_data
    audio_processor.process_and_queue_chunk()

    # Check that a temp file was created and wave file was written
    mkstemp_mock.assert_called_once()
    wave_open_mock.assert_called_once()

    # Verify the queue has one item and it's the expected data
    assert not audio_processor.processing_queue.empty(), "Processing queue should have one item"
    queued_data, _, _ = audio_processor.processing_queue.get()
    assert queued_data == mock_data, "Queued data should match the original audio buffer"
