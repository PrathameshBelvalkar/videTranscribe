# Audio Transcription API

This is a Flask-based API for transcribing audio files into subtitles in both `.srt` and `.vtt` formats using OpenAI's Whisper model.

## Features

- Upload an audio file and receive transcriptions in `.srt` and `.vtt` formats.
- Supports CUDA for faster transcription if a compatible GPU is available.
- Automatically deletes the uploaded audio file after transcription.

## Requirements

- Python 3.10 or higher
- The required Python packages (see the [Installation](#installation) section)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/PrathameshBelvalkar/videoTranscribe.git
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the Flask server, run:

```bash
python app.py
```

The API will be accessible a `http://127.0.0.1:5000`

## API Endpoints

### 1. Upload an Audio File for Transcription

- Endpoint: /upload
- Method: POST
- Description: Upload an audio file (e.g., .mp3, .wav) to be transcribed into .srt and .vtt subtitle formats.

Request

- Content-Type: multipart/form-data
- Form Data:
  - file: The audio file to be uploaded.

Response

- Status Code: 200 OK on success, 400 Bad Request or 500 Internal Server Error on failure.
- Content-Type: application/json

Response Body

```
{
  "status": "success",
  "message": "Transcription completed successfully",
  "data": {
    "srt_url": "http://127.0.0.1:5000/uploads/uploads/1692443567/audio.srt",
    "vtt_url": "http://127.0.0.1:5000/uploads/uploads/1692443567/audio.vtt"
  },
  "timestamp": 1692443567,
  "file_info": {
    "original_filename": "audio.mp3",
    "transcription_model": "base",
    "generated_files": ["audio.srt", "audio.vtt"]
  }
}
```

- Error Responses:
  - 400 Bad Request if the file is not provided or is invalid.
  - 500 Internal Server Error if there is an issue during processing.

### 2. Download Transcription Files

- Endpoint: /uploads/<path:filename>
- Method: GET
- Description: Retrieve the generated subtitle files in .srt or .vtt format.

Request

- Path Parameter: filename - The path to the subtitle file.

Response

- Status Code: 200 OK on success, 500 Internal Server Error on failure.
- Content-Type: Varies based on the file being requested.

### License

This project is licensed under the MIT License.

### Summary

- **Installation Instructions**: Explains how to set up the application.
- **API Endpoints**: Detailed documentation of the available API endpoints, including request and response formats.
- **Directory Structure**: Overview of the files and directories in the project.
- **Error Handling**: Information on how the API handles errors.
- **Contributing and License**: Guidance for contributing to the project and licensing information.

This documentation will help users understand how to use your API and how to set up the project locally.
