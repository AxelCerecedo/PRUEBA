import tkinter as tk
from tkinter import ttk
import time
import pandas as pd
import requests
from tkinter import Tk, messagebox, filedialog
import threading

def validar_urls_csv(ruta_csv, columna_url, columna_resultado, progress_bar, progress_window):
    try:
        # Lee el archivo CSV
        df = pd.read_csv(ruta_csv)

        # Verifica si la columna de URLs existe
        if columna_url not in df.columns:
            raise ValueError(f"La columna '{columna_url}' no se encuentra en el archivo CSV.")

        # Crea la columna de resultados si no existe, o la convierte a tipo texto
        if columna_resultado not in df.columns:
            df[columna_resultado] = ""  # Crea una columna vacía
        else:
            df[columna_resultado] = df[columna_resultado].astype("object")  # Convierte a tipo texto

        # Configuración de la barra de progreso
        progress_bar['maximum'] = len(df)

        # Itera sobre las URLs en el CSV
        for index, row in df.iterrows():
            url = row[columna_url]
            if pd.isna(url):
                df.at[index, columna_resultado] = "URL no válida"
                continue

            try:
                # Verifica si la URL contiene el patrón típico de WordPress
                if "wp-content" in url or "wp-includes" in url:
                    # Comprueba si la URL es accesible
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        df.at[index, columna_resultado] = "OK"
                    else:
                        df.at[index, columna_resultado] = "ERROR"
                else:
                    df.at[index, columna_resultado] = "No es WordPress"
            except requests.RequestException:
                df.at[index, columna_resultado] = "Error al acceder"

            # Actualiza la barra de progreso
            progress_bar['value'] += 1
            progress_window.update_idletasks()

        # Sobrescribe el archivo original con los resultados
        df.to_csv(ruta_csv, index=False)
        messagebox.showinfo("Aviso", f"El archivo '{ruta_csv}' ha sido modificado con el resultado de cada validación de URL, reviselo.")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")
    finally:
        progress_window.destroy()

def progreso_proceso(ruta_csv, columna_url, columna_resultado):
    # Crear y mostrar la ventana con la barra de progreso
    progress_window = tk.Toplevel(root)
    progress_window.title("Validando URLs...")

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
    label_text = tk.Label(progress_window, text="Espere un momento mientras se validan las URLs.", font=("Arial",11), fg="black")
    label_text.pack(pady=10)

    # Traer la ventana al frente y mantenerla en primer plano
    progress_window.attributes('-topmost', True)
    progress_window.update()

    # Iniciar la validación en un hilo separado para no bloquear la interfaz de usuario
    threading.Thread(target=validar_urls_csv, args=(ruta_csv, columna_url, columna_resultado, progress_bar, progress_window)).start()

# Configuración de Tkinter
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

# Seleccionar archivo CSV
try:
    # Nombre de la columna que contiene las URLs
    columna_url = "url"
    # Nombre de la columna donde se guardarán los resultados
    columna_resultado = "validacion"
    
    messagebox.showinfo("Aviso", "Seleccione el archivo.csv (Sintaxis: identificador - "+columna_url+" - "+columna_resultado+") con las URL´s que desea validar y espere un momento, esto puede tardar según el volumen de información a validar. De clic en Aceptar para comenzar.")
    ruta_csv = filedialog.askopenfilename(
        title="Seleccione el archivo CSV con URLs",
        filetypes=[("Archivos CSV", "*.csv")]
    )
    
    if ruta_csv:
        progreso_proceso(ruta_csv, columna_url, columna_resultado)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")
except Exception as e:
    messagebox.showerror("Error", f"Se produjo un error: {e}")

root.mainloop()
