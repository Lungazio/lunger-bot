import yt_dlp
from pydub import AudioSegment
from pydub.playback import play
import threading

# prompt the user to enter a query or use a default value
query = input("Enter a YouTube search query (or press Enter to use 'viva la vida'): ") or 'viva la vida'

# set up yt-dlp options
ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'keepvideo': True,  # add this option to keep the original video file
}


# search for and download audio using yt-dlp
with yt_dlp.YoutubeDL(ytdl_options) as ydl:
    search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
    video_url = search_results['entries'][0]['webpage_url']
    info_dict = ydl.extract_info(video_url, download=False)
    audio_file = ydl.prepare_filename(info_dict)
    ydl.download([video_url])

# load audio using pydub
audio = AudioSegment.from_file(audio_file)

# define a function to play the audio in a separate thread
def play_audio():
    play(audio)

# start a new thread to play the audio
thread = threading.Thread(target=play_audio)
thread.start()
