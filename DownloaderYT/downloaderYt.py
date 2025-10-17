# downloaderYt.py (Substituído com yt-dlp)
from sys import argv
import yt_dlp
import os


try:
    link = argv[1]
except IndexError:
    print("Erro: Por favor, forneça o link do vídeo como argumento.")
    exit()

output_dir = 'Downloads'
output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

ydl_opts = {
    'outtmpl': output_template,
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'print_to_file': {'info_json': os.devnull},
    'quiet': False, 
    'noprogress': True,
}

try:
    os.makedirs(output_dir, exist_ok=True)
    
    with yt_dlp.YoutubeDL({'skip_download': True, 'quiet': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        
    print("Iniciando download...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    
    print("Download completed!")

except Exception as e:
    print(f"Ocorreu um erro durante o download: {e}")