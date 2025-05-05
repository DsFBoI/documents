import tkinter as tk
from tkinter import messagebox
from gui import EsteganografiaApp
from gui_desc import DescifradoApp

class SelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Esteganografía - Selección de Modo")
        self.build_menu()

    def build_menu(self):
        tk.Label(self.root, text="¿Qué desea hacer?", font=("Helvetica", 14)).pack(pady=10)

        cifrar_btn = tk.Button(self.root, text="Cifrar Mensaje", width=30, command=self.abrir_cifrado)
        cifrar_btn.pack(pady=10)

        descifrar_btn = tk.Button(self.root, text="Descifrar Imagen", width=30, command=self.abrir_descifrado)
        descifrar_btn.pack(pady=10)

        salir_btn = tk.Button(self.root, text="Salir", width=30, command=self.root.quit)
        salir_btn.pack(pady=10)

    def abrir_cifrado(self):
        self.root.withdraw()  # Oculta la ventana principal
        ventana_cifrado = tk.Toplevel()
        app = EsteganografiaApp(ventana_cifrado)
        ventana_cifrado.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_subventana(ventana_cifrado))

    def abrir_descifrado(self):
        self.root.withdraw()
        ventana_descifrado = tk.Toplevel()
        app = DescifradoApp(ventana_descifrado)
        ventana_descifrado.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_subventana(ventana_descifrado))

    def cerrar_subventana(self, ventana):
        ventana.destroy()
        self.root.deiconify()  # Muestra la ventana principal otra vez

if __name__ == "__main__":
    root = tk.Tk()
    app = SelectorApp(root)
    root.mainloop()

