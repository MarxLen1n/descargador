import os
import sys
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple

from version import VERSION

REPO = "marxlen1n/descargador"


def obtener_release() -> dict:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    return r.json()

def hay_actualizacion() -> Tuple[bool, dict]:
    try:
        release = obtener_release()

        ultima = release["tag_name"].lstrip("v")

        return ultima != VERSION, release
    except Exception:
        return False, None

def nombre_asset() -> str:
    if sys.platform.startswith("win"):
        if "tui" in Path(sys.argv[0]).name:
            return "descargador-tui-windows.exe"
        return "descargador-gui-windows.exe"

    if "tui" in Path(sys.argv[0]).name:
        return "descargador-tui-linux"

    return "descargador-gui-linux"

def descargar_actualizacion(release) -> str:
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

def reemplazar_binario(nuevo_archivo) -> None:
    print(1)
    actual = Path(sys.argv[0]).resolve()

    print(2)
    if sys.platform.startswith("win"):
        print(3)
        bat = actual.with_suffix(".bat")

        bat.write_text(f"""
@echo off
timeout /t 2 > nul
move /Y "{nuevo_archivo}" "{actual}"
start "" "{actual}"
del "%~f0"
""")

        print(4)
        subprocess.Popen(
            ["cmd", "/c", str(bat)],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        print(5)
        sys.exit()

    else:
        os.chmod(nuevo_archivo, 0o755)

        os.replace(nuevo_archivo, actual)

        os.execv(actual, sys.argv)

if __name__ == "__main__":
    actualizacion, release = hay_actualizacion()

    if not actualizacion:
        print("No hay actualizaciones disponibles.")
        sys.exit()

    print(f"Hay una nueva versión disponible: {release['tag_name']}. Descargando actualización...")

    try:
        nuevo_binario = descargar_actualizacion(release)
        print("Actualización descargada. Reemplazando binario...")
        reemplazar_binario(nuevo_binario)
    except Exception as e:
        print(f"Error al actualizar: {e}")