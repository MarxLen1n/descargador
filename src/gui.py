import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import threading

from downloader import descargar, OPCIONES_BASE, FORMATOS, guardar_opciones, ruta_base

COLORES = {
    "fondo": "#abb2bf",
    "texto": "#282c34",
    "boton": "#61afef",
    "boton_hover": "#528bff",
}

class Ventana:
    def __init__(self, root: tk.Tk):
        ### Ventana
        self.root = root

        root.configure(bg=COLORES["fondo"])
        root.title("Descargador de YouTube")
        root.geometry("400x200")

        ### Widgets
        ventana = tk.Frame(root, padx=20, pady=10, bg=COLORES["fondo"])
        ventana.pack()

        # Menu de formatos
        barra_superior = tk.Menu(root)
        root.config(menu=barra_superior)

        formato = tk.StringVar(value="mp4")
        if OPCIONES_BASE.get("format") == FORMATOS["mp3"]:
            formato.set("mp3")

        menu_formatos = tk.Menu(barra_superior)
        menu_formatos.add_radiobutton(label="MP3", variable=formato, value="mp3", command=lambda: barra_superior.entryconfig(1, label="Formato: MP3"))
        menu_formatos.add_radiobutton(label="MP4", variable=formato, value="mp4", command=lambda: barra_superior.entryconfig(1, label="Formato: MP4"))

        barra_superior.add_cascade(label=f"Formato: {formato.get().upper()}", menu=menu_formatos)

        # Menu carpeta
        barra_superior.add_command(label="Configurar carpeta", command=self.configurar_carpeta)

        # Entrada url
        mensaje_url = tk.Label(ventana, text="URL del video o playlist:", bg=COLORES["fondo"], fg=COLORES["texto"])
        mensaje_url.pack(anchor="w")
        entrada_url = tk.Entry(ventana, width=50)
        entrada_url.pack()

        # Botó de descarga
        botones = tk.Frame(ventana, bg=COLORES["fondo"])
        botones.pack(pady=10)

        boton_descargar = tk.Button(botones, text="Descargar", bg=COLORES["boton"], fg=COLORES["texto"], activebackground=COLORES["boton_hover"], command=lambda: self.iniciar_descarga(entrada_url.get(), formato.get()))
        boton_descargar.pack(pady=10, side="left")

        boton_cancelar = tk.Button(botones, text="Cancelar", bg=COLORES["boton"], fg=COLORES["texto"], activebackground=COLORES["boton_hover"], command=lambda: self.cancelar())
        boton_cancelar.pack(pady=10, side="right")

        # Barra de progreso
        OPCIONES_BASE["progress_hooks"] = [self.progreso_hook]
        self.progreso = tk.DoubleVar()

        self.barra = ttk.Progressbar(
            ventana,
            variable=self.progreso,
            maximum=100,
            length=300
        )
        self.barra.pack(pady=10)

        self.descargando = False
        self.cancelar_descarga = False
        
    def iniciar_descarga(self, url: str, formato: str):
        if self.descargando:
            messagebox.showwarning("Descarga en progreso", "Ya hay una descarga en curso. Por favor espera a que termine.")
            return
        
        self.progreso.set(0)
        self.descargando = True
        self.cancelar_descarga = False

        threading.Thread(
            target=self.descargar, 
            args=(url, formato), 
            daemon=True).start()

    def descargar(self, url: str, formato: str):
        try:
            descargar(url, formato, OPCIONES_BASE)
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "Descarga completada."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

        self.progreso.set(0)
        self.descargando = False

    def configurar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de descargas", initialdir=os.path.expanduser("~"))
        if carpeta:
            OPCIONES_BASE["outtmpl"] = os.path.join(carpeta, "%(title)s.%(ext)s")
            guardar_opciones(OPCIONES_BASE, ruta_base("opciones_base.json"))
            messagebox.showinfo("Configuración guardada", f"Carpeta de descargas configurada a:\n{carpeta}")

    def progreso_hook(self, d: dict):
        if self.cancelar_descarga:
            raise Exception("Descarga cancelada por el usuario.")

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            descargado = d.get("downloaded_bytes", 0)

            if total:
                porcentaje = (descargado / total) * 100
                self.root.after(0, lambda p=porcentaje: self.progreso.set(p))

    def cancelar(self):
        if not self.descargando:
            messagebox.showinfo("Cancelar", "No hay ninguna descarga en curso.")
            return

        self.cancelar_descarga = True
        

if __name__ == "__main__":
    root = tk.Tk()
    Ventana(root)
    root.mainloop()