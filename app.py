from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import logging

app = Flask(__name__)

# Allow requests from specific origins
CORS(app, origins=["https://media-downloader-mauve.vercel.app", "http://127.0.0.1:5500"])

# Directory for saving downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Function to download audio from YouTube
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{uuid.uuid4()}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            if filename.endswith(".webm"):
                filename = filename.replace(".webm", ".mp3")  # Handle ffmpeg audio conversion
            return filename
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        return f"Error: {str(e)}"

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return '', 200

    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file = download_audio(link)
    if downloaded_file.startswith("Error"):
        return jsonify({"error": downloaded_file}), 500

    try:
        # Serve the file as an attachment
        return send_file(downloaded_file, as_attachment=True)
    except Exception as e:
        logging.error(f"File serving error: {e}")
        return jsonify({"error": f"File download failed: {str(e)}"}), 500
    finally:
        # Clean up downloaded file
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
