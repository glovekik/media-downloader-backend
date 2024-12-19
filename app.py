from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Directory for saving downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download audio from YouTube
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            return os.path.basename(filename)  # Return the filename
    except Exception as e:
        return str(e)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file = download_audio(link)
    if "Error" in downloaded_file:
        return jsonify({"error": downloaded_file}), 500

    return jsonify({"message": "Download completed", "filename": downloaded_file})

@app.route('/downloads/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
