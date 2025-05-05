# pip install openai yt-dlp
from openai import OpenAI
import yt_dlp
import os
import sys

def speech_to_text(url: str) -> str:
    """
    Convert speech from a video URL to text using OpenAI's API.
    args:
        url (str): The URL of the video to transcribe.
    returns:
        str: The transcribed text from the video, or an error message.
    """

    # Define the output path for the audio file
    audio_filepath = "downloaded_audio.wav"

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3', # yt-dlp extracts to mp3 first
        'outtmpl': audio_filepath.rsplit('.', 1)[0] + '.%(ext)s', # Use the base name for the template
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    print(f"Attempting to download audio from {url}...")
    downloaded_file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file_path = audio_filepath

            # Check if the file was actually created
            if not os.path.exists(downloaded_file_path):
                 original_ext = info_dict.get('ext')
                 if original_ext:
                     original_download_path = audio_filepath.rsplit('.', 1)[0] + '.' + original_ext
                     if os.path.exists(original_download_path):
                         # If original exists but wav doesn't, postprocessing might have failed
                         print(f"Warning: WAV file not found, but original {original_download_path} exists. Postprocessing might have failed.")
                         downloaded_file_path = original_download_path # Try to use the original if WAV failed
                     else:
                          raise FileNotFoundError(f"Downloaded audio file not found at expected path: {downloaded_file_path}")
                 else:
                    raise FileNotFoundError(f"Downloaded audio file not found at expected path: {downloaded_file_path}")


        print(f"Downloaded audio file: {downloaded_file_path}")

    except Exception as e:
        print(f"An error occurred during download: {e}", file=sys.stderr)
        return f"Error downloading audio: {e}. Please check the URL and ensure yt-dlp can access the video."


    transcription_text = "Error in transcription." # Default error message
    try:
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            print(f"Transcribing audio file: {downloaded_file_path}...")
            client = OpenAI()
            with open(downloaded_file_path, "rb") as audio_file_object:
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe", 
                    file=audio_file_object
                )
                transcription_text = "Text Extracted from video: " + transcription.text
        else:
             transcription_text = "Error: Audio file not found after download attempt."


    except Exception as e:
        print(f"An error occurred during transcription: {e}", file=sys.stderr)
        transcription_text = f"Error in transcription: {e}. Please make sure the video is not too long or the audio is clear."

    finally:
        # Clean up the downloaded audio file
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            try:
                os.remove(downloaded_file_path)
                print(f"Removed downloaded file: {downloaded_file_path}")
            except OSError as e:
                print(f"Error removing file {downloaded_file_path}: {e}", file=sys.stderr)

    return transcription_text

if __name__ == "__main__":
    url = "https://www.bilibili.com/video/BV1wfVPziELe/" 

    text = speech_to_text(url)
    print(text)
