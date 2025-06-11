import pandas as pd
import tkinter as tk
from tkinter import ttk
import time
import requests
from tkinter import Tk, messagebox, filedialog
import threading

def despipepizar(ruta_csv, progress_bar, progress_window):
    progress_bar['value'] = 10
    progress_window.update_idletasks()
    
    # Leer el archivo CSV con la opción low_memory=False para evitar la advertencia de tipo de datos
    df = pd.read_csv(ruta_csv, low_memory=False)
    progress_bar['value'] = 20
    progress_window.update_idletasks()

    # Obtener el nombre de la primera columna
    a_col = df.columns[0]
    # Obtener el nombre de la segunda columna
    b_col = df.columns[1]
    doc_col = "special_document"
    attach_col = "special_attachments"
    
    # Dividir la columna de attachments por '|'
    df[attach_col] = df[attach_col].str.split('|')
    progress_bar['value'] = 30
    progress_window.update_idletasks()
    
    # Explode el DataFrame para que cada elemento de la lista tenga su propia fila
    df = df.explode(attach_col)
    progress_bar['value'] = 40
    progress_window.update_idletasks()
    
    # Eliminar filas donde la columna de attachments está vacía
    df = df[df[attach_col].notna() & (df[attach_col] != '')]
    progress_bar['value'] = 50
    progress_window.update_idletasks()

    # Crear una lista para almacenar el resultado final
    final_result = []

    progress_bar['value'] = 60
    progress_window.update_idletasks()
    
    # Agrupar por id y agregar los special_attachments en una lista
    for item_id, group in df.groupby(a_col):
        # Obtener el valor de special_document para el grupo actual
        special_document = group.iloc[0][doc_col]
        special_document = special_document.replace("file:", "")
        
        # Agregar una fila para special_document
        final_result.append({a_col: item_id, b_col: group.iloc[0][b_col], 'Imagenes': special_document})
        
        # Agregar las filas de special_attachments al resultado final
        for attachment in group[attach_col]:
            final_result.append({a_col: item_id, b_col: group.iloc[0][b_col], 'Imagenes': attachment})
     

    progress_bar['value'] = 70
    progress_window.update_idletasks()
    
    # Convertir la lista a un DataFrame
    final_result_df = pd.DataFrame(final_result)

    # Eliminar las últimas 2 filas del DataFrame
    final_result_df = final_result_df.iloc[:-2]

    # Reordenar las columnas para que la columna de id sea la primera columna
    final_result_df = final_result_df[[a_col, b_col, 'Imagenes']]

    progress_bar['value'] = 80
    progress_window.update_idletasks()
    
    
    # Solicitar al usuario que seleccione la ubicación y el nombre del archivo para guardar el resultado
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Guardar archivo CSV")

    progress_bar['value'] = 90
    progress_window.update_idletasks()
    
    # Guardar el resultado en el archivo CSV seleccionado por el usuario
    final_result_df.to_csv(save_path, index=False)

    # Actualizar la barra de progreso
    progress_bar['value'] = 100
    progress_window.update_idletasks()    
    # Cerrar la ventana de progreso
    progress_window.destroy()
    
    # Mostrar un mensaje de éxito en una ventana emergente
    messagebox.showinfo("Éxito", "El resultado ha sido guardado en '{}'.".format(save_path))

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

    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", style="TProgressbar")
    progress_bar.pack(pady=20)

    # Agregar un efecto de texto en la ventana de progreso
    label_text = tk.Label(progress_window, text="Espere un momento mientras se procesan los datos.", font=("Arial", 11), fg="black")
    label_text.pack(pady=10)

    # Traer la ventana al frente y mantenerla en primer plano
    progress_window.attributes('-topmost', True)
    progress_window.update()

    # Iniciar la validación en un hilo separado para no bloquear la interfaz de usuario
    threading.Thread(target=despipepizar, args=(ruta_csv, progress_bar, progress_window)).start()


# Configuración de Tkinter
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

try:
    # Mostrar un mensaje de Carga archivo en una ventana emergente
    messagebox.showinfo("Información", "Seleccione el archivo.csv que descargó de TAINACAN.")
    # Solicitar al usuario que seleccione el archivo CSV
    ruta_csv = filedialog.askopenfilename(title="Seleccione el archivo CSV", filetypes=[("CSV files", "*.csv")])

    if ruta_csv:
        # Aplicar la función
        progreso_proceso(ruta_csv)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")
except Exception as e:
    messagebox.showerror("Error", f"Se produjo un error: {e}")

root.mainloop()