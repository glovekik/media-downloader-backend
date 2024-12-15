import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to download the audio from a YouTube video
def download_audio(link):
    # yt-dlp options for downloading the best available audio
    ydl_opts = {
        'format': 'bestaudio/best',           # Download the best available audio format
        'outtmpl': 'audio_download.%(ext)s',   # Output file name (with extension)
        'noplaylist': True,                   # Download only the single video (not the playlist)
        'quiet': False,                       # Show download progress in the logs
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])  # Download the audio
        return "Download Finished!"  # Return success message
    except Exception as e:
        return f"Error: {e}"  # Return error message if something goes wrong

# Define the endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # Get the JSON data from the frontend
    link = data.get('link')    # Extract the YouTube link from the JSON request
    if not link:
        return jsonify({"error": "No link provided"}), 400  # Return an error if no link is provided
    result = download_audio(link)  # Call the download function for the given link
    return jsonify({"message": result})  # Return the result (success or error) as a JSON response

if __name__ == "__main__":
    app.run(debug=True)
