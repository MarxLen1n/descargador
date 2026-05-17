import platform, os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading

from downloader import FORMATOS, descargar, OPCIONES_BASE, cargar_ajustes, guardar_ajustes, ruta_base
from updater import hay_actualizacion, descargar_actualizacion
from version import VERSION

COLORES = {
    "fondo": "#abb2bf",
    "texto": "#282c34",
    "boton": "#61afef",
    "boton_hover": "#528bff",
}

class Ventana:
    def __init__(self, root: tk.Tk, ajustes: dict) -> None:
        ### Ventana
        self.root = root
        self.ajustes = ajustes

        root.configure(bg=COLORES["fondo"])
        root.title(f"Descargador de YouTube v{VERSION}")
        root.geometry("400x200")

        ### Widgets
        ventana = tk.Frame(root, padx=20, pady=10, bg=COLORES["fondo"])
        ventana.pack()

        # Menu de formatos
        barra_superior = tk.Menu(root)
        root.config(menu=barra_superior)

        formato = tk.StringVar(value=ajustes.get("formato_predeterminado", "mp3"))

        menu_formatos = tk.Menu(barra_superior)
        for formato in FORMATOS.keys():
            menu_formatos.add_radiobutton(label=formato.upper(), variable=formato, value=formato, command=lambda f=formato: barra_superior.entryconfig(1, label=f"Formato: {f.upper()}"))

        barra_superior.add_cascade(label=f"Formato: {formato.get().upper()}", menu=menu_formatos)

        # Menu carpeta
        barra_superior.add_command(label="Configurar carpeta", command=self.configurar_carpeta)

        # Entrada url
        mensaje_url = tk.Label(ventana, text="URL del video o playlist:", bg=COLORES["fondo"], fg=COLORES["texto"])
        mensaje_url.pack(anchor="w")
        entrada_url = tk.Entry(ventana, width=50)
        entrada_url.pack()

        # Botón de descarga
        botones = tk.Frame(ventana, bg=COLORES["fondo"])
        botones.pack(pady=10)

        self.boton_descargar = tk.Button(botones, text="Descargar", bg=COLORES["boton"], fg=COLORES["texto"], activebackground=COLORES["boton_hover"], command=lambda: self.iniciar_descarga(entrada_url.get(), formato.get()))
        self.boton_descargar.pack(pady=10, side="left")

        self.boton_cancelar = tk.Button(botones, text="Cancelar", bg=COLORES["boton"], fg=COLORES["texto"], activebackground=COLORES["boton_hover"], command=lambda: self.cancelar(), state=tk.DISABLED)
        self.boton_cancelar.pack(pady=10, side="right")

        # Barra de progreso
        marco_progreso = tk.Frame(ventana, bg=COLORES["fondo"])
        marco_progreso.pack(pady=10)

        OPCIONES_BASE["progress_hooks"] = [self.progreso_hook]
        self.progreso = tk.DoubleVar()

        self.barra = ttk.Progressbar(
            marco_progreso,
            variable=self.progreso,
            maximum=100,
            length=300
        )
        self.barra.grid(row=0, column=0, padx=5)

        # Información de descarga
        self.info_descarga = tk.Label(marco_progreso, text="", bg=COLORES["fondo"], fg=COLORES["texto"])
        self.info_descarga.grid(row=1, column=0, pady=5)

        # Actualizaciones
        actualizacion, release = hay_actualizacion()
        if actualizacion:
            if messagebox.askyesno("Actualización disponible", f"Hay una nueva versión disponible: {release['tag_name']}. ¿Quieres descargarla?"):
                try:
                    descargar_actualizacion(release)
                    messagebox.showinfo("Actualización descargada", "La actualización se ha descargado y se instalará al reiniciar el programa.")
                except Exception as e:
                    messagebox.showerror("Error de actualización", f"No se pudo descargar la actualización: {str(e)}")

        self.descargando = False
        self.cancelar_descarga = False
        
    def iniciar_descarga(self, url: str, formato: str):
        if self.descargando:
            messagebox.showwarning("Descarga en progreso", "Ya hay una descarga en curso. Por favor espera a que termine.")
            return
        
        self.boton_descargar.config(state=tk.DISABLED)
        self.boton_cancelar.config(state=tk.NORMAL)
        self.progreso.set(0)
        self.descargando = True
        self.cancelar_descarga = False

        threading.Thread(
            target=self.descargar, 
            args=(url, formato), 
            daemon=True).start()

    def descargar(self, url: str, formato: str):
        self.ajustes["formato_predeterminado"] = formato
        try:
            descargar(url, formato, OPCIONES_BASE)
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "Descarga completada."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

        self.root.after(0, lambda: self.progreso.set(0))
        self.root.after(0, lambda: self.info_descarga.config(text=""))
        self.root.after(0, lambda: self.boton_descargar.config(state=tk.NORMAL))
        self.descargando = False

    def configurar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de descargas", initialdir=os.path.expanduser(self.ajustes.get("carpeta_descargas", "~")))
        if carpeta:
            OPCIONES_BASE["outtmpl"] = os.path.join(carpeta, "%(title)s.%(ext)s")
            self.ajustes["carpeta_descargas"] = carpeta
            messagebox.showinfo("Configuración guardada", f"Carpeta de descargas configurada a:\n{carpeta}")

    def progreso_hook(self, d: dict):
        if self.cancelar_descarga:
            raise Exception("Descarga cancelada por el usuario.")

        if d["status"] == "downloading":
            info_descarga = {}

            info_descarga["total"] = d.get("total_bytes") or d.get("total_bytes_estimate")
            info_descarga["descargado"] = d.get("downloaded_bytes", 0)
            info_descarga["velocidad"] = d.get("speed", 0)
            info_descarga["eta"] = d.get("eta", 0)

            if info_descarga["total"]:
                porcentaje = (info_descarga["descargado"] / info_descarga["total"]) * 100
                self.root.after(0, lambda p=porcentaje: self.progreso.set(p))
                self.root.after(0, lambda: self.barra.update())

                self.root.after(0, lambda: self.info_descarga.config(text=self.procesar_info_descarga(info_descarga)))

    def procesar_info_descarga(self, info_descarga: dict) -> str:
        descargado = info_descarga.get("descargado", 0)
        total = info_descarga.get("total", 0)
        velocidad = info_descarga.get("velocidad", 0)
        eta = info_descarga.get("eta", 0)

        texto = f"{descargado/1024/1024:.2f}MB / {total/1024/1024:.2f}MB | {velocidad/1024:.1f} KB/s | ETA: {eta}s"
        return texto

    def cancelar(self):
        if not self.descargando:
            messagebox.showinfo("Cancelar", "No hay ninguna descarga en curso.")
            return

        self.cancelar_descarga = True
        self.boton_cancelar.config(state=tk.DISABLED)
        self.boton_descargar.config(state=tk.NORMAL)
        self.progreso.set(0)
        self.info_descarga.config(text="")
        self.descargando = False

    def on_closing(self):
        if self.descargando and not messagebox.askokcancel("Salir", "Hay una descarga en curso. ¿Quieres salir de todas formas?"):
            return

        self.cancelar_descarga = True
        guardar_ajustes(self.ajustes)
        self.root.destroy()

def main():
    # Configurar ruta de ffmpeg en Windows
    if platform.system() == "Windows":
        RUTA_FFMPEG = os.path.join(ruta_base(), "ffmpeg")

        os.environ["PATH"] += os.pathsep + RUTA_FFMPEG

        OPCIONES_BASE["ffmpeg_location"] = RUTA_FFMPEG

    # Iniciar descargador
    ajustes = cargar_ajustes()

    root = tk.Tk()
    Ventana(root, ajustes)
    root.mainloop()

if __name__ == "__main__":
    main()