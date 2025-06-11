import pandas as pd
import tkinter as tk
from tkinter import ttk
import time
import pandas as pd
import requests
from tkinter import Tk, messagebox, filedialog
import threading

def procesar_csv(ruta_csv, progress_bar, progress_window):
    try:
        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(ruta_csv)

        # Configurar los nombres de las columnas
        columna_id = "identificador"
        columna_valores = "url"

        # Validar que las columnas existan
        if columna_id not in df.columns or columna_valores not in df.columns:
            raise ValueError(f"Las columnas especificadas ({columna_id} - {columna_valores}) no existen en el archivo CSV.")

        # Agrupar por la columna ID y concatenar los valores
        df['Concatenado'] = df.groupby(columna_id)[columna_valores].transform(lambda x: '||'.join(map(str, x)))
        
        progress_bar['value'] = 10
        
        # Dividir la columna concatenada en dos: primera parte y resto
        df['special_document'] = df['Concatenado'].apply(lambda x: f"file:{x.split('||')[0].strip()}")
        df['special_attachments'] = df['Concatenado'].apply(lambda x: '||'.join(x.split('||')[1:]))

        # Eliminar duplicados para que solo quede un registro por ID
        df_resultado = df.drop_duplicates(subset=[columna_id]).copy()

        # Eliminar la columna 'Concatenado' y la columna de valores
        df_resultado = df_resultado.drop(columns=['Concatenado', columna_valores])

        progress_bar['value'] = 50

        # Seleccionar el archivo CSV con los identificadores adicionales
        messagebox.showinfo("Aviso", "Seleccione el archivo.csv con los special_item_id de Tainacan (No olvide renombrar su columna de referencia con el nombre: identificador). Dicho archivo lo descarga de la sección de exportaciones en Tainacan de su repositorio Digital.")
        ruta_csv_ids = filedialog.askopenfilename(
            title="Seleccione el archivo.csv con los special_item_id de Tainacan",
            filetypes=[("Archivos CSV", "*.csv")]
        )

        if not ruta_csv_ids:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV con los special_item_id de Tainacan.")
            return

        # Cargar el archivo de identificadores adicionales en un DataFrame
        df_ids = pd.read_csv(ruta_csv_ids)

        # Validar que las columnas existan en el archivo de identificadores
        if 'identificador' not in df_ids.columns or 'special_item_id' not in df_ids.columns:
            raise ValueError("El archivo de identificadores debe contener las columnas 'identificador' y 'special_item_id'.")

        # Realizar la combinación de los DataFrames usando identificador de archivo con datos concatenados y identificador del archivo Tainacan
        df_merged = df_resultado.merge(df_ids[['identificador', 'special_item_id']], left_on='identificador', right_on='identificador', how='left')

        progress_bar['value'] = 70

        # Mover la columna 'special_item_id' a la segunda posición
        if 'special_item_id' in df_merged.columns:
            columnas = df_merged.columns.tolist()  # Obtener todas las columnas
            columnas.remove('special_item_id')  # Remover 'special_item_id' de su posición actual
            columnas.insert(1, 'special_item_id')  # Insertar 'special_item_id' en la posición deseada
            df_merged = df_merged[columnas]  # Reordenar el DataFrame

        # Generar un nuevo archivo CSV con los resultados
        nueva_ruta_csv = ruta_csv.replace('.csv', '_procesado.csv')
        df_merged.to_csv(nueva_ruta_csv, index=False)
        # Actualiza la barra de progreso
        progress_bar['value'] = 100
        progress_window.update_idletasks()
        
        messagebox.showinfo("Proceso completado", f"El archivo CSV ha sido procesado correctamente y guardado como {nueva_ruta_csv}.")

    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")
    finally:
        progress_window.destroy()

        
        
def progreso_proceso(ruta_csv):
    # Crear y mostrar la ventana con la barra de progreso
    progress_window = tk.Toplevel(root)
    progress_window.title("Procesando datos...")

    # Centrar la ventana en la pantalla
    window_width = 400
    window_height = 150
    screen_width = progress_window.winfo_screenwidth()
    screen_height = progress_window.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    progress_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Crear un estilo personalizado para la barra de progreso
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar",
                    troughcolor='black',
                    background='orange',
                    thickness=30)

    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", style="Orange.Horizontal.TProgressbar")
    progress_bar.pack(pady=20)

    # Agregar un efecto de texto en la ventana de progreso
    label_text = tk.Label(progress_window, text="Espere un momento mientras se procesan los datos.", font=("Arial",11), fg="black")
    label_text.pack(pady=10)

    # Traer la ventana al frente y mantenerla en primer plano
    progress_window.attributes('-topmost', True)
    progress_window.update()

    # Iniciar la validación en un hilo separado para no bloquear la interfaz de usuario
    threading.Thread(target=procesar_csv, args=(ruta_csv, progress_bar, progress_window)).start()

# Configuración de Tkinter
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

try:
    # Seleccionar archivo CSV
    messagebox.showinfo("Aviso", "Seleccione el archivo.csv (Sintaxis: identificador - url) que tiene las URL a agrupar.")
    ruta_csv = filedialog.askopenfilename(
        title="Seleccione el archivo CSV que tiene las URL a concatenar",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    if ruta_csv:
        progreso_proceso(ruta_csv)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")
except Exception as e:
    messagebox.showerror("Error", f"Se produjo un error: {e}")

root.mainloop()