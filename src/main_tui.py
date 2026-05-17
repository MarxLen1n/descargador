import argparse, os, platform

from downloader import descargar, cargar_ajustes, guardar_ajustes, ruta_base, OPCIONES_BASE, FORMATOS

def progreso(d: dict):
    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        descargado = d.get("downloaded_bytes", 0)
        velocidad = d.get("speed", 0)
        eta = d.get("eta", 0)

        if total:
            porcentaje = descargado / total * 100
            print(
                f"\r{porcentaje:5.1f}% | "
                f"{descargado/1024/1024:.2f}MB / {total/1024/1024:.2f}MB | "
                f"{velocidad/1024:.1f} KB/s | ETA: {eta}s",
                end=""
            )

    elif d["status"] == "finished":
        print("\nProcesando...")

def parser(ajustes: dict):
    ### Crear parser
    parser = argparse.ArgumentParser(description="Descargador de videos y audios de YouTube")

    parser.add_argument("url", help="URL del video o playlist a descargar")
    parser.add_argument("-f", "--formato", default=ajustes.get("formato_predeterminado", "mp3"), choices=FORMATOS.keys(), help="Formato de descarga")
    parser.add_argument("-o", "--output", default=ajustes.get("carpeta_descargas", "descargas"), help="Carpeta de salida")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    OPCIONES_BASE["outtmpl"] = os.path.join(args.output, "%(title)s.%(ext)s")
    OPCIONES_BASE["progress_hooks"] = [progreso]

    try:
        descargar(args.url, args.formato, OPCIONES_BASE)
        print("\nDescarga completada.")
    except Exception as e:
        print(f"\nError: {e}")

    guardar_ajustes({"carpeta_descargas": args.output, "formato_predeterminado": args.formato})

def main():
    # Configurar ruta de ffmpeg en Windows
    if platform.system().lower() == "windows":
        RUTA_FFMPEG = os.path.join(ruta_base(), "ffmpeg")

        os.environ["PATH"] += os.pathsep + RUTA_FFMPEG

        OPCIONES_BASE["ffmpeg_location"] = RUTA_FFMPEG

    # Iniciar descargador
    ajustes = cargar_ajustes()
    parser(ajustes)

if __name__ == "__main__":
    main()