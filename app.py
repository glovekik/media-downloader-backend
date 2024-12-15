import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to download the audio from a YouTube video
def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',          # Download the best available audio format
        'outtmpl': 'audio_download.%(ext)s',  # Output file name (with extension)
        'noplaylist': True,                  # Download only the single video (not the whole playlist)
        'quiet': False,                      # Show progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])  # Download the audio
        return "Download Finished!"  # Success message
    except Exception as e:
        return f"Error: {e}"  # Error message

# Define the endpoint for downloading audio
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # Get the JSON data from the frontend
    link = data.get('link')    # Extract the YouTube link
    if not link:
        return jsonify({"error": "No link provided"}), 400  # Return an error if no link is provided
    result = download_audio(link)  # Call the download function
    return jsonify({"message": result})  # Return the result as JSON

if __name__ == "__main__":
    app.run(debug=True)
