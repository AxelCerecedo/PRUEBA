import os
import pandas as pd
from tkinter import Tk, simpledialog, messagebox
from tkinter.filedialog import askopenfilename, askdirectory

def renombrar_archivos_desde_csv(ruta_archivo_csv, carpeta):
    try:
        # Lee el archivo CSV en un DataFrame
        df = pd.read_csv(ruta_archivo_csv)

        # Verifica si las columnas requeridas existen
        if 'nombre_origen' not in df.columns or 'nuevo_nombre' not in df.columns:
            raise ValueError("El archivo CSV debe tener las columnas 'nombre_origen' y 'nuevo_nombre'.")

        # Itera sobre cada fila del DataFrame
        for index, row in df.iterrows():
            nombre_origen = row['nombre_origen']
            nuevo_nombre = row['nuevo_nombre']

            # Recorre todas las subcarpetas
            archivo_encontrado = False
            for root, dirs, files in os.walk(carpeta):
                print(f"Buscando en: {root}")  # Mensaje de depuración
                ruta_origen = os.path.join(root, nombre_origen)
                if os.path.exists(ruta_origen):
                    ruta_nueva = os.path.join(root, nuevo_nombre)
                    os.rename(ruta_origen, ruta_nueva)
                    print(f"{nombre_origen} renombrado a {nuevo_nombre} en {root}")
                    archivo_encontrado = True
                    break  # Sale del bucle si encuentra el archivo
            if not archivo_encontrado:
                print(f"Archivo {nombre_origen} no encontrado en ninguna subcarpeta de {carpeta}")
    except Exception as e:
        print(f"Se produjo un error: {e}")

# Oculta la ventana principal de Tkinter
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

try:
    messagebox.showinfo("Aviso", "Seleccione el archivo CSV (Sintaxis: nombre_origen - nuevo_nombre ) que contiene el listado de nombres.")
    # Pide al usuario seleccionar el archivo CSV
    ruta_archivo_csv = askopenfilename(
        title="Seleccione el archivo CSV con los nombres...",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    if ruta_archivo_csv:
        # Pide al usuario seleccionar la carpeta con los archivos a renombrar
        messagebox.showinfo("Aviso", "Seleccione la CARPETA que contiene los ARCHIVOS a RENOMBRAR.")
        carpeta = askdirectory(title="Seleccione la CARPETA con los ARCHIVOS a RENOMBRAR")

        if carpeta:
            # Llama a la función para renombrar los archivos
            renombrar_archivos_desde_csv(ruta_archivo_csv, carpeta)
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ninguna carpeta.")
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")

except Exception as e:
    print(f"Se produjo un error: {e}")
