import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from desencrip import extract_hash_from_dct, search_match_with_byte_tolerance
import mysql.connector

class DescifradoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descifrado Esteganográfico")
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

        # Selección de imagen
        self.select_button = tk.Button(root, text="Seleccionar Imagen", command=self.seleccionar_imagen)
        self.select_button.grid(row=5, column=0, pady=10)

        self.image_label = tk.Label(root, text="Ninguna imagen seleccionada")
        self.image_label.grid(row=5, column=1, columnspan=2)

        # Botón de descifrado
        self.decrypt_button = tk.Button(root, text="Descifrar", command=self.procesar_descifrado)
        self.decrypt_button.grid(row=6, column=1, pady=10)

        # Campo de resultado
        tk.Label(root, text="Mensaje descifrado:").grid(row=7, column=0)
        self.result_text = tk.Text(root, height=4, width=40)
        self.result_text.grid(row=7, column=1, columnspan=2)

    def seleccionar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[("JPEG Files", "*.jpg;*.jpeg")])
        if path:
            self.image_path = path
            self.image_label.config(text=os.path.basename(path))

    def procesar_descifrado(self):
        if not self.image_path:
            messagebox.showerror("Error", "Debe seleccionar una imagen para descifrar.")
            return

        # Copiar imagen a ubicación esperada
        os.makedirs("./src/image", exist_ok=True)
        destino = os.path.abspath("./src/image/output.jpeg")

        if os.path.abspath(self.image_path) != destino:
            try:
                shutil.copy(self.image_path, destino)
            except Exception as e:
                messagebox.showerror("Error al copiar la imagen", str(e))
                return

        try:
            conn = mysql.connector.connect(
                host=self.host_entry.get(),
                port=int(self.port_entry.get()),
                user=self.user_entry.get(),
                password=self.password_entry.get(),
                database=self.db_entry.get()
            )
            cursor = conn.cursor()
            cursor.execute("SELECT " + ", ".join([f"byte{i}" for i in range(16)]) + ", message FROM messages ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                messagebox.showinfo("Resultado", "No hay mensajes en la base de datos.")
                return

            for row in rows:
                reference_hash = ''.join(f"{b:02x}" for b in row[:-1])
                extracted_hash = extract_hash_from_dct(destino, reference_hash=reference_hash)
                if extracted_hash:
                    mensaje = self.buscar_mensaje(extracted_hash)
                    if mensaje:
                        self.result_text.delete("1.0", tk.END)
                        self.result_text.insert(tk.END, mensaje)
                    else:
                        self.result_text.delete("1.0", tk.END)
                        self.result_text.insert(tk.END, "[!] Hash no encontrado.")
                    return

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "[!] No se pudo extraer ningún hash válido.")

        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error: {e}")

    def buscar_mensaje(self, extracted_hash):
        try:
            conn = mysql.connector.connect(
                host=self.host_entry.get(),
                port=int(self.port_entry.get()),
                user=self.user_entry.get(),
                password=self.password_entry.get(),
                database=self.db_entry.get()
            )
            cursor = conn.cursor()
            byte_chunks = [int(extracted_hash[i:i+2], 16) for i in range(0, len(extracted_hash), 2)]
            cursor.execute(f"SELECT {', '.join([f'byte{i}' for i in range(16)])}, message FROM messages")
            rows = cursor.fetchall()
            conn.close()

            from hash_utils import compare_hashes
            best_match = None
            highest_similarity = -1

            for row in rows:
                db_bytes = row[:-1]
                db_message = row[-1]
                db_hash = ''.join(f"{b:02x}" for b in db_bytes)
                similarity = compare_hashes(extracted_hash, db_hash)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = db_message

            return best_match

        except Exception as e:
            print("Error al buscar mensaje:", e)
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = DescifradoApp(root)
    root.mainloop()
