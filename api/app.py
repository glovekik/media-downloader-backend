from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from datetime import datetime
import os

# Create the Flask app
app = Flask(__name__)

# Configure CORS to allow frontend from https://glovekik.github.io
CORS(app, origins=["https://glovekik.github.io"], methods=["GET", "POST", "OPTIONS"], supports_credentials=True)

# Ensure the 'downloads' directory exists
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download audio from YouTube
def download_audio(link):
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s-{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            return f"Download Finished! File: {ydl.prepare_filename(info_dict)}"
    except yt_dlp.utils.DownloadError as e:
        return f"Download Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Define endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        link = data.get('link')

        # Validate the YouTube link
        if not link:
            return jsonify({"error": "No link provided"}), 400
        if not link.startswith("https://www.youtube.com"):
            return jsonify({"error": "Invalid YouTube link"}), 400

        # Perform the audio download
        result = download_audio(link)
        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
