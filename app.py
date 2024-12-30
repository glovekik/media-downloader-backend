from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Directory for saving downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download audio from YouTube
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{uuid.uuid4()}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'cookiefile': '/path/to/cookies.txt',  # Add cookies for restricted videos
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            return filename  # Return full file path
    except Exception as e:
        error_message = f"Download error: {e}"
        print(error_message)
        return {"error": error_message}

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
        return jsonify({"error": "Invalid YouTube link"}), 400

    downloaded_file = download_audio(link)
    if isinstance(downloaded_file, dict):  # Check if an error occurred
        return jsonify(downloaded_file), 500

    if not os.path.exists(downloaded_file):
        return jsonify({"error": "File not found after download"}), 500

    try:
        # Serve the file
        response = send_file(downloaded_file, as_attachment=True)
        os.remove(downloaded_file)  # Remove the file after serving
        return response
    except Exception as e:
        return jsonify({"error": f"File download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
