from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Directory for downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download audio
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
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

        # Validate the link
        if not link:
            return jsonify({"error": "No link provided"}), 400
        if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
            return jsonify({"error": "Invalid YouTube link"}), 400

        # Download the audio
        file_path = download_audio(link)
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
