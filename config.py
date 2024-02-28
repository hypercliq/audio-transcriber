# Configuration settings for the AudioTranscriber application

# Model size to use for Whisper transcription. Options: "tiny", "base", "small", "medium", "large"
MODEL_SIZE = "base"

# Sample rates to consider for testing device capabilities (in Hz)
SAMPLE_RATES = [8000, 16000, 32000, 44100, 48000]

# Default frames per buffer for audio stream
FRAMES_PER_BUFFER = 1024

# Default recording duration in seconds
RECORDING_DURATION = 5

# Max retry attempts for the Whisper API
MAX_RETRIES = 3
