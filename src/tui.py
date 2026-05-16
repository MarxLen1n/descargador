import argparse, os

from downloader import descargar, guardar_opciones, ruta_base, OPCIONES_BASE, FORMATOS

def progreso(d):
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

def parser(opciones: dict = None):
    ### Crear parser
    parser = argparse.ArgumentParser(description="Descargador de videos y audios de YouTube")

    parser.add_argument("url", help="URL del video o playlist a descargar")
    parser.add_argument("-f", "--formato", default=opciones.get("formato_predeterminado", "mp3") if opciones else "mp3", choices=FORMATOS.keys(), help="Formato de descarga")
    parser.add_argument("-o", "--output", default=opciones.get("carpeta_descargas", "descargas") if opciones else "descargas", help="Carpeta de salida")

    args = parser.parse_args()

    OPCIONES_BASE["outtmpl"] = os.path.join(args.output, "%(title)s.%(ext)s")
    OPCIONES_BASE["progress_hooks"] = [progreso]


    try:
        descargar(args.url, args.formato, OPCIONES_BASE)
        print("\nDescarga completada.")
    except Exception as e:
        print(f"\nError: {e}")

    guardar_opciones({"carpeta_descargas": args.output, "formato_predeterminado": args.formato}, ruta_base("ajustes.json"))

if __name__ == "__main__":
    parser()