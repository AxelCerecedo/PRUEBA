import os
import tkinter as tk
from tkinter import filedialog, messagebox

def normalizar_extensiones(directory):
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Split the file name and extension
                base, ext = os.path.splitext(file)
                # Create the new file name with lowercase extension
                new_file = base + ext.lower()
                # Rename the file
                os.rename(os.path.join(root, file), os.path.join(root, new_file))
        messagebox.showinfo("Operación exitosa", "Todas las extensiones de los archivos de la carpeta "+directory+" fueron modificados, revise dicha carpeta y de ser necesario refresque o actualice el contenido.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrio un error: {e}")

# Create a Tkinter root window (it will not be shown)
root = tk.Tk()
root.withdraw()

# Ask the user to select a directory
messagebox.showinfo("Aviso", "Selecccione la carpeta con  los archivos a normalizar.")
directory = filedialog.askdirectory(title="Selecccione la carpeta con  los archivos a normalizar.")

# Change all extensions to lowercase if a directory is selected
if directory:
    normalizar_extensiones(directory)
else:
    messagebox.showwarning("Alerta", "No se selecciono ninguna carpeta.")
