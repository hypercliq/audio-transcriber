from unittest.mock import MagicMock, patch

import pytest

from src.whisper_transcription import WhisperTranscription


# Fixture to create a mock of WhisperTranscription for testing
@pytest.fixture
def mock_whisper_transcription():
    # Mock the load_model method of whisper and its transcribe method
    # The transcribe method is set to return a predefined transcription result
    with patch("whisper.load_model", return_value=MagicMock()) as mock_model:
        mock_model.return_value.transcribe.return_value = {
            "text": "mock transcription",
            "segments": [
                {"words": [{"word": "mock", "start": 0, "end": 1, "probability": 1.0}]}
            ],
        }
        transcription = WhisperTranscription("small", 16000)
        yield transcription  # yield the mock object for testing
        transcription.stop_processing()  # cleanup after test


# Test to verify the queue_not_empty method
def test_queue_not_empty(mock_whisper_transcription):
    # Initially, the processing queue should be empty
    assert not mock_whisper_transcription.queue_not_empty()
    # After adding an item to the queue, it should not be empty
    mock_whisper_transcription.processing_queue.put(
        ("audio_chunk", "temp_file_path", 0)
    )
    assert mock_whisper_transcription.queue_not_empty()


# Test to verify the transcribe_audio_chunk method
def test_transcribe_audio_chunk(mock_whisper_transcription):
    with patch("os.remove") as mock_remove:
        # Call the method with a mock file path and check if the file gets removed
        mock_whisper_transcription.transcribe_audio_chunk("temp_file_path", 0)
        mock_remove.assert_called_once_with("temp_file_path")
        # Check if the transcription result is added to the results list
        assert len(mock_whisper_transcription.transcription_results) == 1
        # Verify the content of the transcription result
        expected_result = {
            "text": "mock transcription",
            "segments": [
                {
                    "words": [
                        {
                            "word": "mock",
                            "start": 0,
                            "end": 1,
                            "probability": 1.0,
                            "volume_db": 0,
                        }
                    ]
                }
            ],
        }
        assert mock_whisper_transcription.transcription_results[0] == expected_result


# Test to verify the process_audio_chunk_volume method
def test_process_audio_chunk_volume(mock_whisper_transcription):
    in_data = b"\x00\x01" * 100  # Mock audio data
    # Check if the method returns a valid volume level for the given audio data
    volume_db = mock_whisper_transcription.process_audio_chunk_volume(in_data)
    assert volume_db > -float("inf")


# Test to verify the append_transcription_result method
def test_append_transcription_result(mock_whisper_transcription):
    result = {
        "text": "test",
        "segments": [
            {"words": [{"word": "hello", "start": 0, "end": 1, "probability": 1.0}]}
        ],
    }
    # Append a transcription result and check if it's added to the results list
    mock_whisper_transcription.append_transcription_result(result, 10)
    assert len(mock_whisper_transcription.transcription_results) == 1
    # Check if the volume level is correctly added to the result
    assert (
        mock_whisper_transcription.transcription_results[0]["segments"][0]["words"][0][
            "volume_db"
        ]
        == 10
    )


# Test to verify the finalize_recording method
def test_finalize_recording(mock_whisper_transcription):
    # Mock audio buffer data
    mock_whisper_transcription.audio_buffer = b"\x00\x01" * 100
    # Call finalize_recording and check if the audio buffer is cleared
    mock_whisper_transcription.finalize_recording()
    assert mock_whisper_transcription.audio_buffer == b""
    # Check if the processing queue contains the final audio chunk
    assert not mock_whisper_transcription.processing_queue.empty()
