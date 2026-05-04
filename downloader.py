import yt_dlp, os

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

if __name__ == "__main__":
    url = input("URL del video: ")
    formato = input("Formato (mp3/mp4): ").lower()
    try:
        descargar(url, formato)
        print("Descarga completada.")
    except Exception as e:
        print(f"Error: {e}")