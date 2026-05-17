import os
import sys
import requests
import tempfile
import subprocess
from pathlib import Path

from version import VERSION

REPO = "marxlen1n/descargador"


def obtener_release():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    return r.json()

def hay_actualizacion():
    try:
        release = obtener_release()

        ultima = release["tag_name"].lstrip("v")

        return ultima != VERSION, release
    except Exception:
        return False, None

def nombre_asset():
    if sys.platform.startswith("win"):
        if "tui" in Path(sys.argv[0]).name:
            return "descargador-tui-windows.exe"
        return "descargador-gui-windows.exe"

    if "tui" in Path(sys.argv[0]).name:
        return "descargador-tui-linux"

    return "descargador-gui-linux"

def descargar_actualizacion(release):
    asset_name = nombre_asset()

    for asset in release["assets"]:
        if asset["name"] == asset_name:
            url = asset["browser_download_url"]
            break
    else:
        raise RuntimeError("No se encontró el binario")

    tmp = tempfile.NamedTemporaryFile(delete=False)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        for chunk in r.iter_content(chunk_size=8192):
            tmp.write(chunk)

    tmp.close()

    return tmp.name

def reemplazar_binario(nuevo_archivo):
    actual = Path(sys.argv[0]).resolve()

    if sys.platform.startswith("win"):
        bat = actual.with_suffix(".bat")

        bat.write_text(f"""
@echo off
timeout /t 2 > nul
move /Y "{nuevo_archivo}" "{actual}"
start "" "{actual}"
del "%~f0"
""")

        subprocess.Popen(
            ["cmd", "/c", str(bat)],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        sys.exit()

    else:
        os.chmod(nuevo_archivo, 0o755)

        os.replace(nuevo_archivo, actual)

        os.execv(actual, sys.argv)