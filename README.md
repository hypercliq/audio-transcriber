# Whisper Audio Transcription

This project utilizes OpenAI's Whisper model to transcribe audio in (almost) real-time. It records audio from the user's microphone, segments the audio into 5-second chunks, and then feeds these chunks to Whisper for transcription. This approach enables continuous audio processing and transcription.

The user can start and pause the recording using the **Space** key and exit the application with the **Esc** key. Upon exiting, the application will either display the transcribed text on the screen or save it to a file, including a word-by-word breakdown of the transcription with timestamps, confidence scores, and volume information for each word. The volume is calculated using the root mean square (RMS) of the audio chunks in which the word was spoken.

## Features

- Real-time audio recording and (almost) real-time transcription.
- Utilizes OpenAI's Whisper model for accurate transcription.
- Provides a word-by-word breakdown of the transcription with timestamps, confidence scores, and volume information.


## Getting Started

### Prerequisites

- Python 3.9 or later.
- `pyenv` and `pyenv-virtualenv` for managing Python versions and virtual environments.
- `pip` for installing Python packages.

### Installation

1. Clone the repository:

```sh
git clone https://github.com/hypercliq/audio-transcriber.git
cd audio-transcriber
```

2. Set up a Python virtual environment using `pyenv`:

```sh
pyenv virtualenv 3.9.0 audio-transcriber-3.9.0
pyenv local audio-transcriber-3.9.0
```

3. Install the required dependencies:

```sh
pip install -r requirements.txt
```

> `PyAudio` may require additional dependencies to be installed on your system. Please refer to the [PyAudio documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/) for more information.

### Usage

To start the transcription, run:

```sh
python main.py
```

- After running the command, you will be prompted to choose the microphone to use from the list of available devices and to select the sample rate from the supported rates for your chosen microphone.
- Press **Space** to toggle recording on and off. This allows you to control when the application is actively recording audio.
- Press **Esc** to safely exit the application. Upon exiting, any remaining audio data will be processed, and the transcription results will either be displayed on the screen or saved to a file, based on your configuration settings.

### Configuration

Adjust project settings, such as the Whisper model size and recording duration, in the `config.py` file.

## Contributing

Contributions to improve the project are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to OpenAI for providing the [Whisper](https://github.com/openai/whisper) model.
- Gratitude to the Python community for its excellent ecosystem of tools and libraries.
