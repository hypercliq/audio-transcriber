# Configuration settings for the AudioTranscriber application

# Model size to use for Whisper transcription. Options: "tiny", "base", "small", "medium", "large"
MODEL_SIZE = "base"

# Language code to use for Whisper transcription
LANGUAGE_CODE = "en"

# Whisper prompt to use for transcription
PROMPT = ""

# Sample rates to consider for testing device capabilities (in Hz)
SAMPLE_RATES = [8000, 16000, 32000, 44100, 48000]

# Default frames per buffer for audio stream
FRAMES_PER_BUFFER = 1024

# Default recording duration in seconds
RECORDING_DURATION = 5

# Max retry attempts for the Whisper API
MAX_RETRIES = 3

# Print the results of the transcription to file
PRINT_TO_FILE = True

# Path to the file to print the transcription results
OUTPUT_FILE_PATH = "transcription_results.json"

# Export raw transcriptions to a file
EXPORT_RAW_TRANSCRIPTIONS = True
