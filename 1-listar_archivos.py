import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
def listar_imagenes_y_guardar_csv(directory):
    try:

        if directory:
            # Inicializa una lista para almacenar los datos
            data = []

            # Recorre la carpeta y sus subcarpetas
            for dirpath, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                        parent_folder = os.path.basename(dirpath)
                        data.append([parent_folder, file])

            # Convierte la lista de datos en un DataFrame de pandas
            df = pd.DataFrame(data, columns=['Carpeta/Subcarpeta', 'Archivo'])

            # Pedir al usuario que seleccione la ubicación y el nombre del archivo CSV a guardar
            messagebox.showinfo("Aviso", "Seleccione la ubicación y el nombre del archivo CSV donde se almacenará el listado.")
            archivo_destino = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Guardar archivo CSV como...")

            if archivo_destino:
                # Guarda el DataFrame en un archivo CSV
                df.to_csv(archivo_destino, index=False)
                messagebox.showinfo("Operación exitosa", f"Datos guardados en '{archivo_destino}'")
            else:
                messagebox.showwarning("Advertencia", "No se seleccionó ninguna ubicación para guardar el archivo.")
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ninguna carpeta.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrio un error: {e}")

# Create a Tkinter root window (it will not be shown)
root = tk.Tk()
root.withdraw()

# Ask the user to select a directory
messagebox.showinfo("Aviso", "Seleccione la carpeta con los archivos a listar.")
directory = filedialog.askdirectory(title="Seleccione la carpeta con los archivos a listar.")

# Change all extensions to lowercase if a directory is selected
if directory:
    listar_imagenes_y_guardar_csv(directory)
else:
    messagebox.showwarning("Alerta", "No se selecciono ninguna carpeta.")
