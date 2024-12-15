import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from urllib.parse import urlparse, urlunparse, parse_qs

app = Flask(__name__)

# Allow cross-origin requests from the frontend
CORS(app, origins=["https://glovekik.github.io"], methods=["GET", "POST"], supports_credentials=True)


# Function to clean the YouTube URL
def clean_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Remove query parameters like 'si' and keep the essential ones
    query = parse_qs(parsed_url.query)
    query.pop('si', None)  # Remove 'si' query parameter (if exists)

    # Rebuild the URL without the 'si' parameter
    cleaned_url = urlunparse(parsed_url._replace(query='&'.join(f'{k}={v[0]}' for k, v in query.items())))

    return cleaned_url


# Function to download the audio from a YouTube video
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best available audio format
        'outtmpl': 'downloads/audio_download.%(ext)s',  # Save to a specific directory
        'noplaylist': True,  # Download only the single video (not the playlist)
        'quiet': False,  # Show download progress in the logs
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])  # Download the audio
        return "Download Finished!"  # Return success message
    except yt_dlp.utils.DownloadError as e:
        return f"Download Error: {str(e)}"  # Return specific download error message
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"  # General error handling


# Define the endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # Get the JSON data from the frontend
    link = data.get('link')  # Extract the YouTube link from the JSON request

    # Check if the link is provided
    if not link:
        return jsonify({"error": "No link provided"}), 400  # Return an error if no link is provided

    # Improved validation for YouTube URLs (accepts youtube.com and youtu.be)
    youtube_regex = r"^(https?://)?(www\.)?(youtube|youtu)\.com/.*$"
    if not re.match(youtube_regex, link):
        return jsonify({"error": "Invalid YouTube link"}), 400

    # Clean the URL (remove unnecessary parameters like 'si')
    cleaned_link = clean_url(link)

    result = download_audio(cleaned_link)  # Call the download function for the cleaned link
    return jsonify({"message": result})  # Return the result (success or error) as a JSON response


if __name__ == "__main__":
    app.run(debug=True)
