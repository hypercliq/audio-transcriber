import pyaudio
import wave
import tempfile
import os
import whisper
import warnings
import audioop
import math
from threading import Thread
from queue import Queue
import time

class AudioTranscriber:
    def __init__(self, model_size="base"):
        # Suppress the FP16 warning
        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
        self.model = whisper.load_model(model_size)
        self.audio_buffer = bytes()
        self.chosen_sample_rate = None        
        self.processing_queue = Queue()
        self.is_processing = True
        self.start_background_transcription()
        self.desired_length = None

    def start_background_transcription(self):
        def process_audio_chunks():
            while self.is_processing or not self.processing_queue.empty():
                if not self.processing_queue.empty():
                    audio_chunk, temp_file_path = self.processing_queue.get()
                    volume_db = self.process_audio_chunk(audio_chunk)
                    try:
                        result = self.model.transcribe(temp_file_path, word_timestamps=True)
                        os.remove(temp_file_path)  # Clean up the temporary file
                        # Assuming 'segments' now includes 'words' with timestamps
                        if "segments" in result:
                            for segment in result["segments"]:
                                if "words" in segment:
                                    for word_info in segment["words"]:
                                        word = word_info["word"]
                                        start_time = word_info["start"]
                                        end_time = word_info["end"]
                                        probability = word_info.get("probability", "N/A")  # Probability might be optional
                                        print(f"Word: {word} (Start: {start_time}s, End: {end_time}s, Probability: {probability}, Volume: {volume_db} dB)")
            
                    except Exception as e:
                        print(f"Error during transcription: {e}")
                else:
                    time.sleep(0.1)  # Sleep briefly to avoid busy waiting

        self.processing_thread = Thread(target=process_audio_chunks)
        self.processing_thread.start()

    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        print("Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"{i}: {info['name']}")
        p.terminate()

    def choose_audio_device(self):
        self.list_audio_devices()
        device_index = int(input("Enter the index of the desired audio device: "))
        return device_index

    def find_supported_sample_rates(self, device_index):
        p = pyaudio.PyAudio()
        sample_rates = [8000, 16000, 32000, 44100, 48000]
        supported_rates = []
        print("Testing supported sample rates for the device...")
        for rate in sample_rates:
            try:
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, input_device_index=device_index, frames_per_buffer=4096)
                stream.close()
                supported_rates.append(rate)
                print(f"Supported: {rate} Hz")
            except Exception as e:
                continue
        p.terminate()
        return supported_rates

    def choose_sample_rate(self, supported_rates):
        print("Supported sample rates: ", supported_rates)
        rate = int(input("Enter the desired sample rate from the list above: "))
        if rate in supported_rates:
            return rate
        else:
            print("Invalid selection. Please choose a rate from the list.")
            return self.choose_sample_rate(supported_rates)

    def process_audio_chunk(self, in_data):
        rms = audioop.rms(in_data, 2)  # Assuming 16-bit audio
        volume_db = 20 * math.log10(rms) if rms > 0 else -float('inf')
        return volume_db

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Accumulate audio data until the buffer is full
        self.audio_buffer += in_data
        if len(self.audio_buffer) >= self.desired_length:
            # Save to temp file and enqueue for processing
            temp_file, temp_file_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_file)
            with wave.open(temp_file_path, 'wb') as wave_file:
                wave_file.setnchannels(1)
                wave_file.setsampwidth(2)
                wave_file.setframerate(self.chosen_sample_rate)
                wave_file.writeframes(self.audio_buffer)
            self.processing_queue.put((self.audio_buffer, temp_file_path))
            self.audio_buffer = bytes()  # Reset the buffer for the next chunk
        return (in_data, pyaudio.paContinue)

    def stop_processing(self):
        self.is_processing = False
        self.processing_thread.join()  # Wait for the processing thread to finish

    def start_recording(self, device_index, sample_rate, frames_per_buffer=1024):
        self.chosen_sample_rate = sample_rate
        self.desired_length = self.chosen_sample_rate * 2 * 5  # Adjust for 16-bit audio

        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.chosen_sample_rate,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=frames_per_buffer,
                            stream_callback=self.audio_callback)
            stream.start_stream()
            print("Recording. Press Ctrl+C to stop.")
            
            # Ensuring the stream is active before entering the loop
            if stream.is_active():
                try:
                    while stream.is_active():
                        time.sleep(0.1)  # Sleep to reduce CPU usage
                except KeyboardInterrupt:
                    print("Stopping recording...")
                except Exception as e:
                    print(f"An error occurred: {e}")
        except Exception as e:
            print(f"Failed to open stream: {e}")
        finally:
            # Ensure resources are always cleaned up
            if 'stream' in locals() and stream.is_active():
                stream.stop_stream()
                stream.close()
            p.terminate()
            print("Recording stopped.")


if __name__ == "__main__":
    transcriber = AudioTranscriber("medium")
    device_index = transcriber.choose_audio_device()
    supported_rates = transcriber.find_supported_sample_rates(device_index)
    if not supported_rates:
        print("No supported sample rates found. Exiting.")
    else:
        chosen_sample_rate = transcriber.choose_sample_rate(supported_rates)
        try:
            transcriber.start_recording(device_index, chosen_sample_rate)
        finally:
            transcriber.stop_processing()  # Ensure threads are cleaned up properly
