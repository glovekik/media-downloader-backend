from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import logging

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for specific origins
CORS(app, origins=["https://media-downloader-mauve.vercel.app", "http://127.0.0.1:5500"])

# Directory for saving downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Function to download audio from YouTube
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{uuid.uuid4()}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'verbose': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File {filename} not found after download.")
            return filename  # Return the full file path
    except Exception as e:
        logging.error(f"Download error: {e}")
        return f"Error: {str(e)}"

# Route for downloading audio
@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        return '', 200

    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file = download_audio(link)
    if "Error" in downloaded_file:
        return jsonify({"error": downloaded_file}), 500

    try:
        # Serve the downloaded file
        return send_file(downloaded_file, as_attachment=True)
    except Exception as e:
        logging.error(f"File serving error: {e}")
        return jsonify({"error": f"File download failed: {str(e)}"}), 500
    finally:
        # Clean up the file after sending
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
