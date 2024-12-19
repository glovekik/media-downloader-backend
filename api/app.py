from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from datetime import datetime
import os
import logging

# Create the Flask app
app = Flask(__name__)

# Configure CORS to allow frontend from https://glovekik.github.io (adjusted for sub-paths)
CORS(app, origins=["https://glovekik.github.io/media-downloader/","http://127.0.0.1:5500"], methods=["GET", "POST", "OPTIONS"], supports_credentials=True)

# Ensure the 'downloads' directory exists or use temporary storage for deployments
DOWNLOAD_DIR = "/tmp/downloads"  # For cloud deployment environments like Vercel
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Set up logging to capture error details
logging.basicConfig(level=logging.DEBUG)

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
        app.logger.error(f"Unexpected error: {str(e)}")  # Log any unexpected errors
        return f"An unexpected error occurred: {str(e)}"

# Define endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        link = data.get('link')

        # Validate the YouTube link (including both youtube.com and youtu.be formats)
        if not link:
            return jsonify({"error": "No link provided"}), 400
        if not (link.startswith("https://www.youtube.com") or link.startswith("https://youtu.be")):
            return jsonify({"error": "Invalid YouTube link"}), 400

        # Perform the audio download
        result = download_audio(link)
        return jsonify({"message": result})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")  # Log the error
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
