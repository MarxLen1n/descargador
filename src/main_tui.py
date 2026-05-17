import argparse, os, platform

from downloader import descargar, cargar_ajustes, guardar_ajustes, ruta_base, OPCIONES_BASE, FORMATOS
from updater import hay_actualizacion, descargar_actualizacion, reemplazar_binario
from version import VERSION

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
    parser = argparse.ArgumentParser(description=f"Descargador de videos y audios de YouTube v{VERSION}")

    parser.add_argument("url", help="URL del video o playlist a descargar")
    parser.add_argument("--actualizar", action="store_true", help="Buscar e instalar actualizaciones")
    parser.add_argument("-f", "--formato", default=ajustes.get("formato_predeterminado", "mp3"), choices=FORMATOS.keys(), help="Formato de descarga")
    parser.add_argument("-o", "--output", default=ajustes.get("carpeta_descargas", "descargas"), help="Carpeta de salida")

    args = parser.parse_args()

    # Actualizar si se solicita
    if args.actualizar:
        actualizacion, release = hay_actualizacion()
        if actualizacion:
            print(f"Hay una nueva versión disponible: {release['tag_name']}. Descargando actualización...")
            try:
                binario = descargar_actualizacion(release)
                reemplazar_binario(binario)
                print("Actualización descargada.")
            except Exception as e:
                print(f"Error al descargar la actualización: {e}")
        else:
            print("No hay actualizaciones disponibles.")
        return

    # Preparar descarga
    os.makedirs(args.output, exist_ok=True)

    OPCIONES_BASE["outtmpl"] = os.path.join(args.output, "%(title)s.%(ext)s")
    OPCIONES_BASE["progress_hooks"] = [progreso]

    # Descargar
    try:
        descargar(args.url, args.formato, OPCIONES_BASE)
        print("\nDescarga completada.")
    except Exception as e:
        print(f"\nError: {e}")

    guardar_ajustes({"carpeta_descargas": args.output, "formato_predeterminado": args.formato})

    # Buscar actualizaciones
    actualizacion, release = hay_actualizacion()
    if actualizacion:
        print(f"\nHay una nueva versión disponible: {release['tag_name']}. Para descargarla, ejecuta el programa con la opción --actualizar.")

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