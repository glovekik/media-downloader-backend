from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app, origins=["https://media-downloader-f6xvt84xm-lovekiks-projects.vercel.app/", "http://127.0.0.1:5500"], supports_credentials=True)

# Directory for saving downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download audio or video
def download_media(link, format):
    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else 'best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            return filename  # Return full file path
    except Exception as e:
        print(f"Download error: {e}")
        return str(e)

@app.route('/download', methods=['OPTIONS', 'POST'])
def download():
    if request.method == 'OPTIONS':
        return '', 204  # Handle CORS preflight request

    data = request.get_json()
    link = data.get('link')
    format = data.get('format')

    if not link or format not in ['mp3', 'mp4']:
        return jsonify({"error": "Invalid link or format"}), 400

    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file = download_media(link, format)
    if "Error" in downloaded_file:
        return jsonify({"error": downloaded_file}), 500

    try:
        # Use send_file to directly serve the downloaded file
        return send_file(downloaded_file, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"File download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
