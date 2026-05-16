import platform, os
import tkinter as tk

from downloader import OPCIONES_BASE, cargar_opciones, guardar_opciones, ruta_base
from tui import parser
from gui import Ventana

if __name__ == "__main__":
    RUTA_CONFIG = ruta_base("opciones_base.json")
    cargar_opciones(RUTA_CONFIG)

    if platform.system() == "Windows":
        RUTA_FFMPEG = os.path.join(ruta_base(), "ffmpeg")

        os.environ["PATH"] += os.pathsep + RUTA_FFMPEG

        OPCIONES_BASE["ffmpeg_location"] = RUTA_FFMPEG

        root = tk.Tk()
        Ventana(root)
        root.mainloop()

    else:
        parser()

    guardar_opciones(OPCIONES_BASE, RUTA_CONFIG)

