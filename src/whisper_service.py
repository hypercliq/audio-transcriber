import json
import os
import time

import whisper

from src.cli_interface import CliInterface
from src.config import (
    EXPORT_RAW_TRANSCRIPTIONS,
    LANGUAGE_CODE,
    MAX_RETRIES,
    MODEL_SIZE,
    OUTPUT_FILE_PATH,
    PRINT_TO_FILE,
    PROMPT,
    TASK,
)


class WhisperService:
    def __init__(self):
        """
        Initialize the WhisperTranscription with the given model size and sample rate.
        :param model_size: The size of the model to use for transcription.
        :param chosen_sample_rate: The sample rate chosen for recording.
        """
        CliInterface.print_info("Loading Whisper model: " + CliInterface.colorize(MODEL_SIZE, bold=True))
        self.model = whisper.load_model(MODEL_SIZE)
        self.results = []  # Accumulate transcription results with volumes
        self.active_tasks = 0

    def transcribe_audio_chunk(self, temp_file_path, volume_db):
        """
        Transcribe an audio chunk from a temporary file.
        :param temp_file_path: The path to the temporary file containing the audio chunk.
        :param volume_db: The volume of the audio chunk in decibels.
        """
        self.active_tasks += 1
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                result = self.model.transcribe(
                    temp_file_path,
                    word_timestamps=True if TASK == "transcribe" else False,
                    language=LANGUAGE_CODE,
                    prompt=PROMPT,
                    task=TASK,
                )
                os.remove(temp_file_path)  # Clean up the temporary file
                self.append_transcription_result(result, volume_db)  # Append result with volume
                break
            except Exception as e:
                CliInterface.print_error(e)
                CliInterface.print_warning(f"Retrying transcription attempt {attempt + 1}...")
                time.sleep(1)  # Adding delay between retries
                attempt += 1
        if attempt == MAX_RETRIES:
            CliInterface.print_error("Failed to transcribe audio chunk.")

        self.active_tasks -= 1

    def append_transcription_result(self, result, volume_db):
        """
        Append a transcription result and its volume to the list of results.
        :param result: The result of the transcription.
        :param volume_db: The volume of the audio chunk in decibels.
        """
        if TASK == "transcribe":
            for segment in result.get("segments", []):
                for word in segment.get("words", []):
                    word["volume_db"] = volume_db
        self.results.append(result)

    def output_transcription_results(self):
        """
        Output the full transcription results, including the full text and information about each word.
        """
        if self.results.__len__() == 0:
            CliInterface.print_warning("No transcription results to output.")
            return
        if EXPORT_RAW_TRANSCRIPTIONS:
            output = self.results
        else:
            full_text = "".join([result["text"] for result in self.results])
            words = (
                [
                    word
                    for result in self.results
                    for segment in result.get("segments", [])
                    for word in segment.get("words", [])
                ]
                if TASK == "transcribe"
                else []
            )
            output = {
                "full_text": full_text,
                "words": words,
            }

        json_output = json.dumps(output, indent=4)

        if PRINT_TO_FILE:
            with open(OUTPUT_FILE_PATH, "w") as file:
                file.write(json_output)
            CliInterface.print_info(
                "Transcription results have been written to: " + CliInterface.colorize(OUTPUT_FILE_PATH, bold=True)
            )
        else:
            CliInterface.print_info("Transcription results:")
            print(json_output)
