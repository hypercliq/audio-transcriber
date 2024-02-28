import audioop
import math
import os
import tempfile
import time
import wave
from queue import Queue
from threading import Thread

import pyaudio
import whisper

from config import MAX_RETRIES, RECORDING_DURATION


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
        self.audio_buffer = (
            bytes()
        )  # Initialize an empty buffer for accumulating audio data
        self.desired_length = chosen_sample_rate * 2 * RECORDING_DURATION
        print(f"Desired length: {self.desired_length}")
        self.start_processing_thread()

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
                audio_chunk, temp_file_path = self.processing_queue.get()
                print(f"Processing audio chunk... (Size: {len(audio_chunk)} bytes)")
                volume_db = self.process_audio_chunk_volume(audio_chunk)
                print(f"Volume: {volume_db} dB")
                self.transcribe_audio_chunk(temp_file_path)
            else:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting

    def transcribe_audio_chunk(self, temp_file_path):
        """
        Transcribe an audio chunk from a temporary file.
        :param temp_file_path: The path to the temporary file containing the audio chunk.
        """
        attempt, max_retries = 0, MAX_RETRIES
        while attempt < max_retries:
            try:
                result = self.model.transcribe(temp_file_path, word_timestamps=True)
                print(f"Transcription result: {result}")
                self.process_transcription_result(result)
                os.remove(temp_file_path)  # Clean up the temporary file
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                attempt += 1
        if attempt == max_retries:
            print("Failed to transcribe after several attempts.")

        print("Completed processing.")

    def process_transcription_result(self, result):
        """
        Process the result of a transcription.
        :param result: The result of the transcription.
        """
        if "segments" in result:
            for segment in result["segments"]:
                self.process_segment(segment)

    def process_segment(self, segment):
        """
        Process a segment from the transcription result.
        :param segment: The segment to process.
        """
        if "words" in segment:
            for word_info in segment["words"]:
                self.print_word_info(word_info)

    def print_word_info(self, word_info):
        """
        Print information about a word from the transcription result.
        :param word_info: The information about the word.
        """
        word = word_info["word"]
        start_time = word_info["start"]
        end_time = word_info["end"]
        probability = word_info.get(
            "probability", "N/A"
        )  # Probability might be optional
        print(
            f"Word: {word} (Start: {start_time}s, End: {end_time}s, Probability: {probability})"
        )

    def process_audio_chunk_volume(self, in_data):
        """
        Calculate the volume of an audio chunk in decibels.
        :param in_data: The audio data.
        :return: The volume of the audio data in decibels.
        """
        rms = audioop.rms(in_data, 2)  # Assuming 16-bit audio
        volume_db = 20 * math.log10(rms) if rms > 0 else -float("inf")
        return volume_db

    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for the audio stream. Adds the incoming audio data to the buffer and processes it when it reaches the desired length.
        :param in_data: The incoming audio data.
        :param frame_count: The number of frames in the audio data.
        :param time_info: Information about the timing of the audio data.
        :param status: The status of the audio stream.
        :return: A tuple containing None and pyaudio.paContinue, indicating that the stream should continue.
        """
        self.audio_buffer += in_data
        if len(self.audio_buffer) >= self.desired_length:
            temp_file, temp_file_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_file)
            with wave.open(temp_file_path, "wb") as wave_file:
                wave_file.setnchannels(1)
                wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(self.chosen_sample_rate)
                wave_file.writeframes(self.audio_buffer)
            self.processing_queue.put((self.audio_buffer, temp_file_path))
            self.audio_buffer = bytes()  # Clear the buffer for the next chunk
        return (None, pyaudio.paContinue)

    def finalize_recording(self):
        """
        Process the remaining audio data in the buffer when the recording is finalized.
        """
        if len(self.audio_buffer) > 0:
            print("Processing the last audio chunk...")
            temp_file, temp_file_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_file)
            with wave.open(temp_file_path, "wb") as wave_file:
                wave_file.setnchannels(1)
                wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(self.chosen_sample_rate)
                wave_file.writeframes(self.audio_buffer)
            self.processing_queue.put((self.audio_buffer, temp_file_path))
            self.audio_buffer = (
                bytes()
            )  # Clear the buffer after processing the last chunk

    def stop_processing(self):
        """
        Stop the processing of audio chunks and wait for the processing thread to finish.
        """
        self.is_processing = False
        self.processing_thread.join()
