import yt_dlp
from pydub import AudioSegment
from rich import print
import subprocess
import os
import requests
from utils.deno_setup import ensure_deno


DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def extract_yt_audio(url:str)->str:
    deno_path = ensure_deno()
    output_path = os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s')
    print("Outbound IP seen by internet:", requests.get('https://api.ipify.org').text)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': False,
        'verbose': True,

        'source_address': '0.0.0.0',

        'js_runtimes': {
            'deno': {
                'path': deno_path
            }
        },
        
        'extractor_args': {
            'youtube': {'player_client': ['mweb']},
            'youtubepot-bgutilhttp': {
                'base_url': [os.getenv("POT_PROVIDER_URL")]
            }
        },

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        base, _ = filepath.rsplit('.', 1)
        filepath = base + '.wav'
        return filepath


def extract_audio(path:str)->str:
    filename = os.path.splitext(os.path.basename(path))[0]
    output_path = os.path.join(DOWNLOADS_DIR, f"{filename}_converted.wav")

    command = [
        'ffmpeg',
        '-i', path,
        '-ac', '1',        # mono (downmix if dual/stereo)
        '-ar', '16000',    # 16kHz sample rate
        '-vn',              # no video stream
        '-y',               # overwrite if exists
        output_path
    ]

    subprocess.run(command, check=True, capture_output=True)
    return output_path

def chunk_audio(audio_path:str, chunk_size:int = 10)->list:
    chunk_ms = chunk_size * 60 * 1000
    audio = AudioSegment.from_wav(audio_path)

    chunks = []
    for i, st in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[st: st+chunk_ms]
        chunk_path = f"{audio_path}_chunk_{i+1}.wav"
        chunk.export(chunk_path, format='wav')
        chunks.append(chunk_path)

    return chunks

def process_audio(audio_path:str)->list:
    if audio_path.startswith("http://") or audio_path.startswith("https://"):
        print("YT Video Detected...")
        print("Extracting Audio...")
        audio_data = extract_yt_audio(audio_path)
    else:
        print("Video Detected...")
        print("Extracting Audio...")
        audio_data = extract_audio(audio_path)

    chunks = chunk_audio(audio_data)
    print(f"Got {len(chunks)} chunk(s).")
    return chunks
