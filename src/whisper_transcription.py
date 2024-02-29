import audioop
import json
import math
import os
import tempfile
import time
import wave
from queue import Queue
from threading import Thread

import pyaudio
import whisper

from src.cli_interface import CliInterface
from src.config import MAX_RETRIES, OUTPUT_FILE_PATH, PRINT_TO_FILE, RECORDING_DURATION


class WhisperTranscription:
    def __init__(self, model_size, chosen_sample_rate):
        """
        Initialize the WhisperTranscription with the given model size and sample rate.
        :param model_size: The size of the model to use for transcription.
        :param chosen_sample_rate: The sample rate chosen for recording.
        """
        self.model = whisper.load_model(model_size)
        self.chosen_sample_rate = chosen_sample_rate
        self.processing_queue = Queue()
        self.is_processing = True
        self.audio_buffer = bytes()  # Initialize an empty buffer for accumulating audio data
        self.desired_length = chosen_sample_rate * 2 * RECORDING_DURATION
        self.transcription_results = []  # Accumulate transcription results with volumes
        self.start_processing_thread()
        self.active_transcribing_tasks = 0

    def queue_not_empty(self):
        """
        Check if the processing queue is not empty.
        :return: True if the queue is not empty, False otherwise.
        """
        return not self.processing_queue.empty()

    def start_processing_thread(self):
        """
        Start a new thread for processing audio chunks.
        """
        self.processing_thread = Thread(target=self.process_audio_chunks_queue)
        self.processing_thread.start()

    def process_audio_chunks_queue(self):
        """
        Continuously process audio chunks from the queue until the processing is stopped.
        """
        while self.is_processing or not self.processing_queue.empty():
            if not self.processing_queue.empty():
                (
                    audio_chunk,
                    temp_file_path,
                    volume_db,
                ) = self.processing_queue.get()  # Adjusted to include volume_db
                self.transcribe_audio_chunk(temp_file_path, volume_db)  # Pass volume_db to the method
                # CliInterface.print_processed_chunk(volume_db, len(audio_chunk))
            else:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting

    def transcribe_audio_chunk(self, temp_file_path, volume_db):
        """
        Transcribe an audio chunk from a temporary file.
        :param temp_file_path: The path to the temporary file containing the audio chunk.
        :param volume_db: The volume of the audio chunk in decibels.
        """
        self.active_transcribing_tasks += 1
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                result = self.model.transcribe(temp_file_path, word_timestamps=True)
                os.remove(temp_file_path)  # Clean up the temporary file
                self.append_transcription_result(result, volume_db)  # Append result with volume
                break
            except Exception as e:
                CliInterface.print_error(e)
                CliInterface.print_transcription_attempt(attempt + 1)
                time.sleep(1)  # Adding delay between retries
                attempt += 1
        if attempt == MAX_RETRIES:
            CliInterface.print_transcription_failed()

        self.active_transcribing_tasks -= 1

    def is_processing_completed(self):
        return self.processing_queue.empty() and self.active_transcribing_tasks == 0

    def process_audio_chunk_volume(self, in_data):
        """
        Calculate the volume of an audio chunk in decibels.
        :param in_data: The audio data.
        :return: The volume of the audio data in decibels.
        """
        rms = audioop.rms(in_data, 2)  # Assuming 16-bit audio
        return 20 * math.log10(rms) if rms > 0 else -float("inf")

    def append_transcription_result(self, result, volume_db):
        """
        Append a transcription result and its volume to the list of results.
        :param result: The result of the transcription.
        :param volume_db: The volume of the audio chunk in decibels.
        """
        for segment in result.get("segments", []):
            for word in segment.get("words", []):
                word["volume_db"] = volume_db
        self.transcription_results.append(result)

    def audio_callback(self, in_data, _frame_count, _time_info, _status):
        """
        Callback function for the audio stream.
        Adds the incoming audio data to the buffer and processes it when it reaches the desired length.
        :param in_data: The incoming audio data.
        :param _frame_count: The number of frames in the audio data.
        :param _time_info: Information about the timing of the audio data.
        :param _status: The status of the audio stream.
        :return: A tuple containing None and pyaudio.paContinue, indicating that the stream should continue.
        """
        self.audio_buffer += in_data
        if len(self.audio_buffer) >= self.desired_length:
            self.process_and_queue_chunk()
        return (None, pyaudio.paContinue)

    def process_and_queue_chunk(self):
        """
        Process an audio chunk from the buffer, calculate its volume, and add it to the queue for transcription.
        """
        temp_file, temp_file_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_file)
        with wave.open(temp_file_path, "wb") as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(self.chosen_sample_rate)
            wave_file.writeframes(self.audio_buffer)
        volume_db = self.process_audio_chunk_volume(self.audio_buffer)
        CliInterface.print_processing_chunk(volume_db, len(self.audio_buffer))
        self.processing_queue.put((self.audio_buffer, temp_file_path, volume_db))  # Ensure this matches the expected unpacking

        self.audio_buffer = bytes()  # Clear the buffer for the next chunk

    def finalize_recording(self):
        """
        Process the remaining audio data in the buffer when the recording is finalized.
        """
        if len(self.audio_buffer) > 0:
            self.process_and_queue_chunk()

    def stop_processing(self):
        """
        Stop the processing of audio chunks and wait for the processing thread to finish.
        """
        self.is_processing = False
        self.processing_thread.join()
        self.output_transcription_results()

    def output_transcription_results(self):
        """
        Output the full transcription results, including the full text and information about each word.
        """
        full_text = " ".join([result["text"] for result in self.transcription_results])
        words = [
            word
            for result in self.transcription_results
            for segment in result.get("segments", [])
            for word in segment.get("words", [])
        ]
        output = {"full_text": full_text, "words": words}
        json_output = json.dumps(output, indent=4)

        if PRINT_TO_FILE:
            with open(OUTPUT_FILE_PATH, "w") as file:
                file.write(json_output)
            CliInterface.print_output_path(OUTPUT_FILE_PATH)
        else:
            CliInterface.print_output(json_output)
