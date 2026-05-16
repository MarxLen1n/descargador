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

def cargar_opciones(ruta: Path) -> dict: # devuelve un diccionario con las opciones + el formato de salida
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            opciones = json.load(f)
    
    OPCIONES_BASE["outtmpl"] = os.join(opciones.get("carpeta_descargas", "descargas"), OPCIONES_BASE["outtmpl"])

    o = OPCIONES_BASE.copy()
    o["formato"] = opciones.get("formato_predeterminado", "mp3")
    return o

def guardar_opciones(opciones: dict, ruta: Path):
    with open(ruta, "w") as f:
        json.dump(opciones, f, indent=4)

def ruta_base(nombre: str = "") -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent

    return base / nombre

def descargar(url: str, formato: str, opciones: dict = None):
    if formato not in FORMATOS:
        raise ValueError("Formato no soportado")

    if opciones is None:
        opciones = OPCIONES_BASE.copy()

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
