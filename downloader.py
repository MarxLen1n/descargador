import yt_dlp
import os, sys, platform
import argparse

###
### DOWNLOADER
###

def progreso(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        descargado = d.get('downloaded_bytes', 0)
        velocidad = d.get('speed', 0)
        eta = d.get('eta', 0)

        if total:
            porcentaje = descargado / total * 100
            print(
                f"\r{porcentaje:5.1f}% | "
                f"{descargado/1024/1024:.2f}MB / {total/1024/1024:.2f}MB | "
                f"{velocidad/1024:.1f} KB/s | ETA: {eta}s",
                end=''
            )

    elif d['status'] == 'finished':
        print("\nProcesando...")

OPCIONES_BASE = {
    'outtmpl': os.path.join('descargas', '%(title)s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
    'windowsfilenames': True,
    'progress_hooks': [progreso],
}

FORMATOS = {
    'mp3': 'bestaudio',
    'mp4': 'bestvideo[height<=1080]+bestaudio/best',
}

def get_base_path():
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(__file__)

if platform.system() == "Windows":
    RUTA_FFMPEG = os.path.join(get_base_path(), "ffmpeg")

    os.environ["PATH"] += os.pathsep + RUTA_FFMPEG

    OPCIONES_BASE['ffmpeg_location'] = RUTA_FFMPEG

def descargar(url: str, formato: str):
    if formato not in FORMATOS:
        raise ValueError("Formato no soportado")

    opciones = OPCIONES_BASE.copy()
    opciones['format'] = FORMATOS[formato]

    if formato == 'mp3':
        opciones['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    if formato == 'mp4':
        opciones['merge_output_format'] = 'mp4'

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])

###
### CLI
###

def crear_parser():
    parser = argparse.ArgumentParser(description="Descargador de videos y audios de YouTube")

    parser.add_argument('url', help="URL del video o playlist a descargar")
    parser.add_argument('-f', '--formato', default='mp3', choices=['mp3', 'mp4'], help="Formato de descarga")
    parser.add_argument("-o", "--output", default="descargas", help="Carpeta de salida")

    return parser

if __name__ == "__main__":
    parser = crear_parser()
    args = parser.parse_args()

    OPCIONES_BASE['outtmpl'] = os.path.join(args.output, '%(title)s.%(ext)s')

    try:
        descargar(args.url, args.formato)
        print("\nDescarga completada.")
    except Exception as e:
        print(f"\nError: {e}")
        