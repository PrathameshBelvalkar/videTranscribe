from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import whisper
import torch

app = Flask(__name__)
CORS(app)


class AudioTranscriber:
    def __init__(self, model_path, audio_path, progress_callback=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        try:
            self.model = whisper.load_model(model_path).to(self.device)
        except Exception as e:
            raise RuntimeError(f"Error loading model: {str(e)}")
        self.audio_path = audio_path
        self.subtitles = []
        self.progress_callback = progress_callback

    def transcribe_audio(self):
        try:
            print("Starting audio transcription...")
            result = self.model.transcribe(self.audio_path, verbose=True)
        except Exception as e:
            raise RuntimeError(f"Error during transcription: {str(e)}")

        total_segments = len(result["segments"])
        for idx, segment in enumerate(result["segments"]):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            self.subtitles.append((start, end, text))
            if self.progress_callback:
                self.progress_callback(text, idx + 1 == total_segments)

        print("Audio transcription complete")
        return self.generate_files()

    def format_timestamp(self, seconds, vtt=False):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        if vtt:
            return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
        else:
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def generate_files(self):
        output_dir = os.path.dirname(self.audio_path)
        base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
        vtt_path = os.path.join(output_dir, f"{base_name}.vtt")
        srt_path = os.path.join(output_dir, f"{base_name}.srt")

        try:
            vtt_content = "WEBVTT\n\n"
            for index, (start, end, text) in enumerate(self.subtitles, start=1):
                vtt_content += f"{index}\n"
                vtt_content += f"{self.format_timestamp(start, vtt=True)} --> {self.format_timestamp(end, vtt=True)}\n"
                vtt_content += f"{text}\n\n"

            with open(vtt_path, "w", encoding="utf-8") as vtt_file:
                vtt_file.write(vtt_content)
            print(f"VTT file generated at {vtt_path}")

            srt_content = ""
            for index, (start, end, text) in enumerate(self.subtitles, start=1):
                srt_content += f"{index}\n"
                srt_content += (
                    f"{self.format_timestamp(start)} --> {self.format_timestamp(end)}\n"
                )
                srt_content += f"{text}\n\n"

            with open(srt_path, "w", encoding="utf-8") as srt_file:
                srt_file.write(srt_content)
            print(f"SRT file generated at {srt_path}")
        except Exception as e:
            raise RuntimeError(f"Error generating subtitle files: {str(e)}")

        try:
            if os.path.exists(self.audio_path):
                os.remove(self.audio_path)
                print(f"Deleted audio file: {self.audio_path}")
        except Exception as e:
            print(f"Warning: Failed to delete audio file: {str(e)}")

        return vtt_path, srt_path


def transcribe(audio_path, model_path="base"):
    try:
        transcriber = AudioTranscriber(model_path, audio_path)
        vtt_path, srt_path = transcriber.transcribe_audio()
        return vtt_path, srt_path
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        timestamp = int(time.time())
        upload_folder = os.path.join("uploads", str(timestamp))
        os.makedirs(upload_folder, exist_ok=True)

        audio_path = os.path.join(upload_folder, "audio.mp3")
        file.save(audio_path)

        vtt_path, srt_path = transcribe(audio_path)

        vtt_url = request.host_url + vtt_path.replace(os.sep, "/")
        srt_url = request.host_url + srt_path.replace(os.sep, "/")

        response = {
            "status": "success",
            "message": "Transcription completed successfully",
            "data": {"srt_url": srt_url, "vtt_url": vtt_url},
            "timestamp": timestamp,
            "file_info": {
                "original_filename": "audio.mp3",
                "transcription_model": "base",
                "generated_files": ["audio.srt", "audio.vtt"],
            },
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


@app.route("/uploads/<path:filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory("uploads", filename)
    except Exception as e:
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
