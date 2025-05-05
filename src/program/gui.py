import tkinter as tk
from tkinter import filedialog, messagebox
import os
from encrip import cifrar
from db_utils import store_hash_and_message_in_db
from hash_utils import generate_hash
import jpeg_toolbox
import numpy as np
import shutil

# ===== Interfaz Gráfica =====

class EsteganografiaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cifrado Esteganográfico")
        self.image_path = None

        # Campos de conexión
        tk.Label(root, text="Host:").grid(row=0, column=0)
        self.host_entry = tk.Entry(root)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1)

        tk.Label(root, text="Puerto:").grid(row=1, column=0)
        self.port_entry = tk.Entry(root)
        self.port_entry.insert(0, "3306")
        self.port_entry.grid(row=1, column=1)

        tk.Label(root, text="Usuario:").grid(row=2, column=0)
        self.user_entry = tk.Entry(root)
        self.user_entry.insert(0, "root")
        self.user_entry.grid(row=2, column=1)

        tk.Label(root, text="Contraseña:").grid(row=3, column=0)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.grid(row=3, column=1)

        tk.Label(root, text="Base de datos:").grid(row=4, column=0)
        self.db_entry = tk.Entry(root)
        self.db_entry.insert(0, "tfg_db")
        self.db_entry.grid(row=4, column=1)

        # Campo mensaje
        tk.Label(root, text="Mensaje:").grid(row=5, column=0)
        self.message_entry = tk.Entry(root, width=40)
        self.message_entry.grid(row=5, column=1, columnspan=2)

        # Imagen
        self.select_button = tk.Button(root, text="Seleccionar Imagen", command=self.seleccionar_imagen)
        self.select_button.grid(row=6, column=0)

        self.image_label = tk.Label(root, text="Ninguna imagen seleccionada")
        self.image_label.grid(row=6, column=1, columnspan=2)

        # Botón procesar
        self.encrypt_button = tk.Button(root, text="Cifrar y Guardar", command=self.procesar)
        self.encrypt_button.grid(row=7, column=1, pady=10)

    def seleccionar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[("JPEG Files", "*.jpg;*.jpeg")])
        if path:
            self.image_path = path
            self.image_label.config(text=os.path.basename(path))

    def procesar(self):
        if not self.image_path or not self.message_entry.get():
            messagebox.showerror("Error", "Debe seleccionar una imagen y escribir un mensaje.")
            return
    
        # Crear carpeta si no existe
        os.makedirs("./src/image", exist_ok=True)
    
        # Ruta destino
        destino = os.path.abspath("./src/image/input.jpeg")
    
        # Solo copiar si son archivos distintos
        if os.path.abspath(self.image_path) != destino:
            try:
                shutil.copy(self.image_path, destino)
            except Exception as e:
                messagebox.showerror("Error al copiar la imagen", str(e))
                return
    
        # Guardar las variables de conexión y mensaje en entorno
        os.environ["DB_HOST"] = self.host_entry.get()
        os.environ["DB_PORT"] = self.port_entry.get()
        os.environ["DB_USER"] = self.user_entry.get()
        os.environ["DB_PASS"] = self.password_entry.get()
        os.environ["DB_NAME"] = self.db_entry.get()
        os.environ["MESSAGE"] = self.message_entry.get()
    
        try:
            cifrar()  # usa la lógica del encrip.py
            messagebox.showinfo("Éxito", "Cifrado completado y guardado en base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = EsteganografiaApp(root)
    root.mainloop()
