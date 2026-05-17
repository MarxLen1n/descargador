from pathlib import Path
import sys

import yt_dlp
import os, json

OPCIONES_BASE = {
    "outtmpl": "%(title)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "windowsfilenames": True,
}

FORMATOS = {
    "mp3": "bestaudio",
    "mp4": "bestvideo[height<=1080]+bestaudio/best",
}

def cargar_ajustes() -> dict: # devuelve un diccionario con los ajustes
    if os.path.exists(ruta_base("ajustes.json")):
        with open(ruta_base("ajustes.json"), "r") as f:
            ajustes = json.load(f)
    else:
        ajustes = {"carpeta_descargas": os.path.join(os.path.expanduser("~"), "Descargas"), "formato_predeterminado": "mp3"}

    if not ajustes.get("carpeta_descargas", None):
        ajustes["carpeta_descargas"] = os.path.join(os.path.expanduser("~"), "Descargas")
    if not ajustes.get("formato_predeterminado", None):
        ajustes["formato_predeterminado"] = "mp3"
    
    OPCIONES_BASE["outtmpl"] = os.path.join(ajustes.get("carpeta_descargas", "descargas"), OPCIONES_BASE["outtmpl"])

    return ajustes

def guardar_ajustes(ajustes: dict) -> None:
    with open(ruta_base("ajustes.json"), "w") as f:
        json.dump(ajustes, f, indent=4)

def ruta_base(nombre: str = "") -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent

    return base / nombre

def descargar(url: str, formato: str, opts: dict) -> None:
    if formato not in FORMATOS:
        raise ValueError("Formato no soportado")

    opciones = opts.copy()

    opciones.pop("postprocessors", None)
    opciones.pop("merge_output_format", None)

    opciones["format"] = FORMATOS[formato]

    if formato == "mp3":
        opciones["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    if formato == "mp4":
        opciones["merge_output_format"] = "mp4"

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])
