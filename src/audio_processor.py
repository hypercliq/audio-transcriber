import audioop
import math
import os
import tempfile
import time
import wave
from queue import Queue
from threading import Thread

import pyaudio

from src.cli_interface import CliInterface
from src.config import CHUNK_DURATION
from src.whisper_service import WhisperService


class AudioProcessor:
    def __init__(self, chosen_sample_rate):
        self.processing_queue = Queue()
        self.audio_buffer = bytes()
        self.desired_length = chosen_sample_rate * 2 * CHUNK_DURATION
        self.chosen_sample_rate = chosen_sample_rate
        self.whisper_transcription = WhisperService()
        self.is_processing = True
        self.processing_thread = Thread(target=self.process_audio_chunks_queue)
        self.processing_thread.start()

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
                self.whisper_transcription.transcribe_audio_chunk(temp_file_path, volume_db)  # Pass volume_db to the method
                CliInterface.print_success(
                    "Processed audio chunk with volume {:.2f} dB and size {} bytes.".format(volume_db, len(audio_chunk))
                )
            else:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting

    def stop_processing(self):
        """
        Stop the processing of audio chunks and wait for the processing thread to finish.
        """
        self.is_processing = False
        self.processing_thread.join()
        self.whisper_transcription.output_transcription_results()

    def is_processing_completed(self):
        """
        Check if the processing of audio chunks is completed.

        :return: True if the processing queue is empty and there are no active tasks in the transcription service.
        """
        return self.processing_queue.empty() and self.whisper_transcription.active_tasks == 0

    def process_audio_chunk_volume(self, in_data):
        """
        Calculate the volume of an audio chunk in decibels.
        :param in_data: The audio data.
        :return: The volume of the audio data in decibels.
        """
        rms = audioop.rms(in_data, 2)  # Assuming 16-bit audio
        return 20 * math.log10(rms) if rms > 0 else -float("inf")

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
        self.processing_queue.put((self.audio_buffer, temp_file_path, volume_db))  # Ensure this matches the expected unpacking

        self.audio_buffer = bytes()  # Clear the buffer for the next chunk

    def finalize_recording(self):
        """
        Process the remaining audio data in the buffer when the recording is finalized.
        """
        if len(self.audio_buffer) > 0:
            self.process_and_queue_chunk()
