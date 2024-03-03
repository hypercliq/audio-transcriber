import warnings

from src.audio_service import AudioService


def main():
    """
    Main function to create an instance of the AudioTranscriber and start it.
    """
    transcriber = AudioService()
    transcriber.run()


if __name__ == "__main__":
    # Suppress the FP16 warning
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
    main()
