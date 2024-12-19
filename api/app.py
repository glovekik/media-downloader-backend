import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://glovekik.github.io/media-downloader/", "http://127.0.0.1:5500"])

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        file_path = ydl.prepare_filename(info_dict)
        return file_path

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        link = data.get('link')

        if not link or not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
            return jsonify({"error": "Invalid YouTube link"}), 400

        file_path = download_audio(link)
        file_name = os.path.basename(file_path)
        return jsonify({"downloadUrl": f"/file/{file_name}"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/file/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
