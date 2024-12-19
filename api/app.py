from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from datetime import datetime
import os
import logging

app = Flask(__name__)
CORS(app, origins=["https://glovekik.github.io", "http://127.0.0.1:5500"], methods=["GET", "POST"], supports_credentials=True)

DOWNLOAD_DIR = "/tmp/downloads"  # Use tmp directory for Railway
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            return os.path.basename(filename)
    except Exception as e:
        app.logger.error(f"Download failed: {str(e)}")
        return None

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    link = data.get('link')
    if not link or not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    filename = download_audio(link)
    if not filename:
        return jsonify({"error": "Failed to download the audio"}), 500

    return jsonify({"message": "Download successful", "downloadUrl": f"/static/{filename}"})

if __name__ == "__main__":
    app.run(debug=True)
