import warnings

from src.audio_transcriber import AudioTranscriber
from src.config import MODEL_SIZE


def main():
    """
    Main function to create an instance of the AudioTranscriber and start it.
    """
    transcriber = AudioTranscriber(model_size=MODEL_SIZE)
    transcriber.run()


if __name__ == "__main__":
    # Suppress the FP16 warning
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
    main()
