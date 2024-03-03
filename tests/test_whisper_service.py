import json
from unittest.mock import Mock, mock_open, patch

import pytest

from src.whisper_service import WhisperService


@pytest.fixture
def whisper_service(mocker):
    mocker.patch("src.whisper_service.whisper.load_model", return_value=Mock())
    mocker.patch("src.whisper_service.PRINT_TO_FILE", True)
    mocker.patch("src.whisper_service.EXPORT_RAW_TRANSCRIPTIONS", False)
    mocker.patch("src.whisper_service.OUTPUT_FILE_PATH", "/path/to/output.json")
    mocker.patch("src.whisper_service.TASK", "transcribe")
    mocker.patch("src.whisper_service.LANGUAGE_CODE", "en")
    mocker.patch("src.whisper_service.PROMPT", "")
    mocker.patch("src.whisper_service.MAX_RETRIES", 3)
    mocker.patch("src.whisper_service.MODEL_SIZE", "base")

    yield WhisperService()


# Test the initialization of WhisperService
def test_whisper_service_initialization(whisper_service):
    assert whisper_service.model is not None
    assert whisper_service.results == []
    assert whisper_service.active_tasks == 0


# Test the transcribe_audio_chunk method
def test_transcribe_audio_chunk(whisper_service):
    temp_file_path = "/path/to/temp_file.wav"
    volume_db = -20

    with patch("src.whisper_service.os.remove") as remove_mock:
        whisper_service.model.transcribe.return_value = {"text": "Hello, world!"}

        whisper_service.transcribe_audio_chunk(temp_file_path, volume_db)

        whisper_service.model.transcribe.assert_called_once_with(
            temp_file_path,
            word_timestamps=True,
            language="en",
            prompt="",
            task="transcribe",
        )
        remove_mock.assert_called_once_with(temp_file_path)
        assert len(whisper_service.results) == 1
        assert whisper_service.results[0] == {"text": "Hello, world!"}


# Test the append_transcription_result method
def test_append_transcription_result(whisper_service):
    result = {
        "segments": [
            {
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 1.0},
                    {"text": "world", "start": 1.0, "end": 2.0},
                ]
            }
        ]
    }
    volume_db = -20

    whisper_service.append_transcription_result(result, volume_db)

    assert len(whisper_service.results) == 1
    assert whisper_service.results[0] == {
        "segments": [
            {
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 1.0, "volume_db": -20},
                    {"text": "world", "start": 1.0, "end": 2.0, "volume_db": -20},
                ]
            }
        ]
    }


# Test the output_transcription_results method
def test_output_transcription_results(whisper_service):
    whisper_service.results = [
        {"text": "Hello"},
        {"text": "world"},
    ]

    m = mock_open()
    with patch("src.whisper_service.open", m, create=True), patch(
        "src.cli_interface.CliInterface.print_info"
    ) as print_info_mock:
        whisper_service.output_transcription_results()

    m.assert_called_once_with("/path/to/output.json", "w")
    handle = m()
    handle.write.assert_called_once_with(json.dumps({"full_text": "Helloworld", "words": []}, indent=4))
    print_info_mock.assert_called_once_with("Transcription results have been written to: \033[1m/path/to/output.json\033[0m")


# Test the output_transcription_results method when there are no results
def test_output_transcription_results_no_results(whisper_service):
    whisper_service.results = []

    with patch("src.cli_interface.CliInterface.print_warning") as print_warning_mock:
        whisper_service.output_transcription_results()

        print_warning_mock.assert_called_once_with("No transcription results to output.")


# Test the output_transcription_results method when EXPORT_RAW_TRANSCRIPTIONS is True
def test_output_transcription_results_export_raw_transcriptions(whisper_service):
    whisper_service.results = [
        {"text": "Hello"},
        {"text": "world"},
    ]

    with patch("src.whisper_service.open", create=True) as open_mock, patch(
        "src.cli_interface.CliInterface.print_info"
    ) as print_info_mock:
        file_mock = Mock()
        open_mock.return_value = file_mock

        with patch("src.whisper_service.PRINT_TO_FILE", False):
            whisper_service.output_transcription_results()

            open_mock.assert_not_called()
            file_mock.write.assert_not_called()
            print_info_mock.assert_called_once_with("Transcription results:")
