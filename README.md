# Python Audio Transcription Project

This project utilizes OpenAI's Whisper model to transcribe audio in (almost) real-time. It records audio from the user's microphone, chunks the audio (5 seconds), and then feeds these chunks to Whisper for transcription. This approach allows for continuous audio processing and transcription.

The result of each chunk's transcription is displayed on the screen as JSON data. Words are timestamped, and the confidence score is also provided.

Each chunk's volume, in decibels, is also displayed on the screen before the transcription.

## Features

- Real-time audio recording and (almost real-time) processing.
- Utilizes OpenAI's Whisper model for accurate transcription.

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

### Usage

To start the transcription, run:

```sh
python main.py
```

- Press **Space** to start/stop recording.
- Press **Esc** to exit the application.

### Configuration

You can adjust the project settings, such as the Whisper model size and recording duration, in the `config.py` file.

## Contributing

Contributions to improve the project are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- OpenAI for providing the Whisper model.
- The Python community for an excellent ecosystem of tools and libraries.
