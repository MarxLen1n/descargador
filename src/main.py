import platform, os
import tkinter as tk

from downloader import OPCIONES_BASE, cargar_ajustes, ruta_base
from tui import parser
from gui import Ventana

if __name__ == "__main__":
    d = cargar_ajustes()

    if platform.system() == "Windows":
        RUTA_FFMPEG = os.path.join(ruta_base(), "ffmpeg")

        os.environ["PATH"] += os.pathsep + RUTA_FFMPEG

        OPCIONES_BASE["ffmpeg_location"] = RUTA_FFMPEG

        root = tk.Tk()
        Ventana(root, d)
        root.mainloop()

    else:
        parser(d)

