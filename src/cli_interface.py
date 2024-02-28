class CliInterface:
    @staticmethod
    def print_welcome():
        print("Welcome to the Whisper Audio Transcription Service")
        print("-------------------------------------------------")
        print("Press Space to start/stop recording, Esc to exit.")

    @staticmethod
    def print_initialize_recording():
        print("Initializing recording...", end="", flush=True)

    @staticmethod
    def print_recording_started():
        print("\r\033[91m●\033[0m Recording started. Press Space to pause...\n")

    @staticmethod
    def print_recording_pausing(stop=False):
        print(
            "\nPausing" if not stop else "\nStopping",
            "recording... please wait for processing to finish.",
        )

    @staticmethod
    def print_recording_paused():
        print("\n\u23F8 Recording paused. Press Space to start or Esc to exit.")

    @staticmethod
    def print_exit():
        print("\nExiting application... Thank you for using our service!")

    @staticmethod
    def print_processing_chunk(volume_db, chunk_size):
        print(
            f"\r>> Processing chunk (Volume: {volume_db:.2f} dB, Size: {chunk_size} bytes)..."
        )

    @staticmethod
    def print_processed_chunk(volume_db, chunk_size):
        print(
            f"\nProcessed audio chunk with volume {volume_db:.2f} dB and size {chunk_size}."
        )

    @staticmethod
    def print_transcription_attempt(attempt):
        print(f"\nTranscription attempt {attempt}...")

    @staticmethod
    def print_transcription_failed():
        print("\nFailed to transcribe after several attempts.")

    @staticmethod
    def print_finalizing():
        print("\nFinalizing recording...")

    @staticmethod
    def print_transcription_complete():
        print("\nTranscription completed successfully.")

    @staticmethod
    def print_error(e):
        print(f"\nError: {e}")

    @staticmethod
    def print_output_path(path):
        print(f"\nTranscription results have been written to: {path}")

    @staticmethod
    def print_output(json_output):
        print(json_output)

    @staticmethod
    def print_devices(devices):
        print("Available audio devices:")
        for index, name in devices:
            print(f"{index}: {name}")

    @staticmethod
    def print_supported_sample_rates(rates):
        print("Testing supported sample rates for the device:")
        for rate in rates:
            print(f"Supported: {rate} Hz")

    @staticmethod
    def print_sample_rate_options(supported_rates):
        print("Supported sample rates: ")
        for i, rate in enumerate(supported_rates, start=1):
            print(f"{i}) {rate} Hz")

    @staticmethod
    def print_invalid_selection():
        print("Invalid selection. Please enter a number from the list.")

    @staticmethod
    def print_enter_number():
        print("Enter the number corresponding to the desired sample rate: ")

    @staticmethod
    def print_invalid_number():
        print("Please enter a valid number.")
