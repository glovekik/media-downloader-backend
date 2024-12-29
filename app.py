from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app, origins=["https://media-downloader-omega.vercel.app", "http://127.0.0.1:5500"])

# Directory for saving downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download media from YouTube
def download_media(link, format):
    extension = "mp3" if format == "mp3" else "mp4"
    ydl_opts = {
        'format': 'bestaudio/best' if format == "mp3" else 'bestvideo+bestaudio',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{uuid.uuid4()}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            base_filename = os.path.basename(filename)
            return filename, base_filename  # Full path and base filename
    except Exception as e:
        print(f"Download error: {e}")
        return str(e), None

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    link = data.get('link')
    format = data.get('format')

    if not link:
        return jsonify({"error": "No link provided"}), 400
    if format not in ["mp3", "mp4"]:
        return jsonify({"error": "Invalid format"}), 400
    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file, base_filename = download_media(link, format)
    if "Error" in downloaded_file:
        return jsonify({"error": downloaded_file}), 500

    try:
        # Use the video title as the filename for download
        download_name = base_filename.rsplit('-', 1)[0] + f".{format}"
        return send_file(downloaded_file, as_attachment=True, download_name=download_name)
    except Exception as e:
        return jsonify({"error": f"File download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
