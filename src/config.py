# Model size to use for Whisper service. Options: "tiny", "base", "small", "medium", "large"
MODEL_SIZE = "base"

# Language code to use for Whisper service, i.e. the language of the audio to transcribe or translate
# If not specified, the language will be automatically detected
LANGUAGE_CODE = "en"

# Whisper prompt to help guide the transcription or translation
PROMPT = ""

# Whether to use the Whisper service for transcription or translation, valid options: "transcribe", "translate"
TASK = "transcribe"

# Sample rates to consider for testing device capabilities (in Hz)
SAMPLE_RATES = [8000, 16000, 32000, 44100, 48000]

# Default frames per buffer for audio stream
FRAMES_PER_BUFFER = 1024

# Default recording chunk size in seconds
CHUNK_DURATION = 5

# Max retry attempts for the Whisper API
MAX_RETRIES = 3

# Print the results of the transcription to file
PRINT_TO_FILE = True

# Path to the file to print the transcription results
OUTPUT_FILE_PATH = "transcription_results.json"

# Output raw transcription either to file or to the console
# If True, the raw output from Whisper will be used for the transcription results
OUTPUT_RAW_TRANSCRIPTION = False
