import warnings

from audio_transcriber import AudioTranscriber
from config import MODEL_SIZE


def main():
    # Create an instance of the AudioTranscriber with the model size from the configuration.
    transcriber = AudioTranscriber(model_size=MODEL_SIZE)

    # Start the transcriber's main loop to listen for key presses and manage recordings.
    transcriber.run()


if __name__ == "__main__":
    # Suppress the FP16 warning
    warnings.filterwarnings(
        "ignore", message="FP16 is not supported on CPU; using FP32 instead"
    )
    main()
