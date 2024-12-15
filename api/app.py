from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

# Configure CORS to allow frontend from https://glovekik.github.io
CORS(app, origins=["https://glovekik.github.io"], methods=["GET", "POST", "OPTIONS"], supports_credentials=True)


# Function to download audio from YouTube
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/audio_download.%(ext)s',
        'noplaylist': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return "Download Finished!"
    except yt_dlp.utils.DownloadError as e:
        return f"Download Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


# Define endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    if not link.startswith("https://www.youtube.com"):
        return jsonify({"error": "Invalid YouTube link"}), 400

    result = download_audio(link)
    return jsonify({"message": result})


if __name__ == "__main__":
    app.run(debug=True)
