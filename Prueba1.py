import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # Asegúrate de tener Pillow instalado
import pygame 
import threading
import pandas as pd
import requests
import os


# =====================================================================
# MÓDULO 1: Normalizar extensiones (poner en minúscula la extensión)
# =====================================================================
def normalizar_extensiones(directory):
    try:
        for app_dir, dirs, files in os.walk(directory):
            for file in files:
                base, ext = os.path.splitext(file)
                new_file = base + ext.lower()
                os.rename(os.path.join(app_dir, file), os.path.join(app_dir, new_file))
        messagebox.showinfo("Operación exitosa",
                            f"Todas las extensiones de la carpeta\n'{directory}' fueron modificadas.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def run_normalizar_extensiones():
    messagebox.showinfo("Aviso", "Seleccione la carpeta con los archivos a normalizar.")
    directory = filedialog.askdirectory(title="Selecciona carpeta")
    if directory:
        normalizar_extensiones(directory)
    else:
        messagebox.showwarning("Alerta", "No se seleccionó ninguna carpeta.")

# =====================================================================
# MÓDULO 2: Listar imágenes y guardar CSV
# =====================================================================
def listar_imagenes_y_guardar_csv(directory):
    try:
        data = []
        for dirpath, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                    parent_folder = os.path.basename(dirpath)
                    data.append([parent_folder, file])
        df = pd.DataFrame(data, columns=['Carpeta/Subcarpeta', 'Archivo'])
        messagebox.showinfo("Aviso", "Seleccione la ubicación y el nombre del archivo CSV donde se almacenará el listado.")
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                title="Guardar archivo CSV")
        if csv_path:
            df.to_csv(csv_path, index=False)
            messagebox.showinfo("Operación exitosa", f"Datos guardados en:\n'{csv_path}'")
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ubicación para guardar el archivo.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def run_listar_imagenes():
    messagebox.showinfo("Aviso", "Seleccione la carpeta con los archivos a listar.")
    directory = filedialog.askdirectory(title="Selecciona carpeta")
    if directory:
        listar_imagenes_y_guardar_csv(directory)
    else:
        messagebox.showwarning("Alerta", "No se seleccionó ninguna carpeta.")

# =====================================================================
# MÓDULO 3: Renombrar archivos desde CSV
# =====================================================================
def renombrar_archivos_desde_csv(ruta_archivo_csv, carpeta):
    try:
        df = pd.read_csv(ruta_archivo_csv)
        if 'nombre_origen' not in df.columns or 'nuevo_nombre' not in df.columns:
            raise ValueError("El CSV debe tener columnas 'nombre_origen' y 'nuevo_nombre'.")
        for index, row in df.iterrows():
            nombre_origen = row['nombre_origen']
            nuevo_nombre = row['nuevo_nombre']
            archivo_encontrado = False
            for app_dir, dirs, files in os.walk(carpeta):
                ruta_origen = os.path.join(app_dir, nombre_origen)
                if os.path.exists(ruta_origen):
                    ruta_nueva = os.path.join(app_dir, nuevo_nombre)
                    os.rename(ruta_origen, ruta_nueva)
                    archivo_encontrado = True
                    break  # Sale al encontrar el primer archivo
            if not archivo_encontrado:
                print(f"Archivo {nombre_origen} no encontrado en {carpeta}")
        messagebox.showinfo("Operación completada", "El proceso de renombrado de archivos finalizó.")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")

def run_renombrar_archivos():
    messagebox.showinfo("Aviso", "Seleccione el archivo CSV con columnas 'nombre_origen' y 'nuevo_nombre'.")
    ruta_csv = filedialog.askopenfilename(title="Selecciona CSV", filetypes=[("CSV files", "*.csv")])
    if not ruta_csv:
        messagebox.showwarning("Advertencia", "No se seleccionó el archivo CSV.")
        return
    messagebox.showinfo("Aviso", "Seleccione la CARPETA que contiene los ARCHIVOS a RENOMBRAR.")
    carpeta = filedialog.askdirectory(title="Selecciona carpeta")
    if carpeta:
        renombrar_archivos_desde_csv(ruta_csv, carpeta)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ninguna carpeta.")

# =====================================================================
# MÓDULO 4: Validar URLs en CSV
# =====================================================================
def validar_urls_csv(ruta_csv, columna_url, columna_resultado, progress_bar, progress_window):
    try:
        df = pd.read_csv(ruta_csv)
        if columna_url not in df.columns:
            raise ValueError(f"La columna '{columna_url}' no se encuentra en el CSV.")
        if columna_resultado not in df.columns:
            df[columna_resultado] = ""
        else:
            df[columna_resultado] = df[columna_resultado].astype("object")
        progress_bar['maximum'] = len(df)
        for index, row in df.iterrows():
            url = row[columna_url]
            if pd.isna(url):
                df.at[index, columna_resultado] = "URL no válida"
                continue
            try:
                if "wp-content" in url or "wp-includes" in url:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        df.at[index, columna_resultado] = "OK"
                    else:
                        df.at[index, columna_resultado] = "ERROR"
                else:
                    df.at[index, columna_resultado] = "No es WordPress"
            except requests.RequestException:
                df.at[index, columna_resultado] = "Error al acceder"
            progress_bar['value'] += 1
            progress_window.update_idletasks()
        df.to_csv(ruta_csv, index=False)
        messagebox.showinfo("Aviso", f"El archivo\n'{ruta_csv}'\nha sido modificado con los resultados de validación.")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")
    finally:
        progress_window.destroy()

def progreso_validar_urls(ruta_csv, columna_url, columna_resultado): 
    prog_window = tk.Toplevel(root)
    prog_window.title("Validando URLs...")
    window_width = 400
    window_height = 150
    screen_width = prog_window.winfo_screenwidth()
    screen_height = prog_window.winfo_screenheight()
    pos_top = int(screen_height/2 - window_height/2)
    pos_right = int(screen_width/2 - window_width/2)
    prog_window.geometry(f"{window_width}x{window_height}+{pos_right}+{pos_top}")
    style = ttk.Style(prog_window)
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor='black', background='orange', thickness=30)
    progress_bar = ttk.Progressbar(prog_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)
    label_text = tk.Label(prog_window, text="Espere mientras se validan las URLs.", font=("Arial", 11))
    label_text.pack(pady=10)
    prog_window.attributes('-topmost', True)
    prog_window.update()
    threading.Thread(target=validar_urls_csv, args=(ruta_csv, columna_url, columna_resultado, progress_bar, prog_window)).start()

def run_validar_urls():
    columna_url = "url"
    columna_resultado = "validacion"
    messagebox.showinfo("Aviso", f"Seleccione el archivo CSV (con columnas: {columna_url} y {columna_resultado}).")
    ruta_csv = filedialog.askopenfilename(title="Selecciona CSV con URLs", filetypes=[("CSV files", "*.csv")])
    if ruta_csv:
        progreso_validar_urls(ruta_csv, columna_url, columna_resultado)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")

# =====================================================================
# MÓDULO 5: Concatenar filas (Agrupar por 'identificador' y unir 'url')
# =====================================================================
def procesar_csv(ruta_csv, progress_bar, progress_window):
    try:
        df = pd.read_csv(ruta_csv)
        columna_id = "identificador"
        columna_valores = "url"
        if columna_id not in df.columns or columna_valores not in df.columns:
            raise ValueError(f"Las columnas '{columna_id}' y '{columna_valores}' no existen en el CSV.")
        df['Concatenado'] = df.groupby(columna_id)[columna_valores].transform(lambda x: '||'.join(map(str, x)))
        progress_bar['value'] = 10
        df['special_document'] = df['Concatenado'].apply(lambda x: f"file:{x.split('||')[0].strip()}")
        df['special_attachments'] = df['Concatenado'].apply(lambda x: '||'.join(x.split('||')[1:]))
        df_resultado = df.drop_duplicates(subset=[columna_id]).copy()
        df_resultado = df_resultado.drop(columns=['Concatenado', columna_valores])
        progress_bar['value'] = 50
        messagebox.showinfo("Aviso", "Seleccione el CSV con los special_item_id de Tainacan.\n(El CSV debe tener columnas: identificador y special_item_id)")
        ruta_csv_ids = filedialog.askopenfilename(title="Selecciona CSV de identificadores", filetypes=[("CSV files", "*.csv")])
        if not ruta_csv_ids:
            messagebox.showwarning("Advertencia", "No se seleccionó el CSV de identificadores.")
            return
        df_ids = pd.read_csv(ruta_csv_ids)
        if 'identificador' not in df_ids.columns or 'special_item_id' not in df_ids.columns:
            raise ValueError("El CSV de identificadores debe tener las columnas 'identificador' y 'special_item_id'.")
        df_merged = df_resultado.merge(df_ids[['identificador', 'special_item_id']], on='identificador', how='left')
        progress_bar['value'] = 70
        if 'special_item_id' in df_merged.columns:
            cols = df_merged.columns.tolist()
            cols.remove('special_item_id')
            cols.insert(1, 'special_item_id')
            df_merged = df_merged[cols]
        nueva_ruta_csv = ruta_csv.replace('.csv', '_procesado.csv')
        df_merged.to_csv(nueva_ruta_csv, index=False)
        progress_bar['value'] = 100
        progress_window.update_idletasks()
        messagebox.showinfo("Proceso completado", f"CSV procesado y guardado como:\n{nueva_ruta_csv}")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")
    finally:
        progress_window.destroy()

def progreso_proceso_concat(ruta_csv):
    prog_window = tk.Toplevel(root) 
    prog_window.title("Procesando datos...")
    window_width = 400
    window_height = 150
    screen_width = prog_window.winfo_screenwidth()
    screen_height = prog_window.winfo_screenheight()
    pos_top = int(screen_height/2 - window_height/2)
    pos_right = int(screen_width/2 - window_width/2)
    prog_window.geometry(f"{window_width}x{window_height}+{pos_right}+{pos_top}")
    style = ttk.Style(prog_window)
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor='black', background='orange', thickness=30)
    progress_bar = ttk.Progressbar(prog_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)
    label_text = tk.Label(prog_window, text="Espere mientras se procesan los datos.", font=("Arial", 11))
    label_text.pack(pady=10)
    prog_window.attributes('-topmost', True)
    prog_window.update()
    threading.Thread(target=procesar_csv, args=(ruta_csv, progress_bar, prog_window)).start()

def run_concatenar_filas():
    messagebox.showinfo("Aviso", "Seleccione el archivo CSV (con columnas 'identificador' y 'url') que desea agrupar.")
    ruta_csv = filedialog.askopenfilename(title="Selecciona CSV", filetypes=[("CSV files", "*.csv")])
    if ruta_csv:
        progreso_proceso_concat(ruta_csv)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")

# =====================================================================
# MÓDULO 6: Despipepizar (Dividir columna de attachments usando '|' y reestructurar)
# =====================================================================
def despipepizar(ruta_csv, progress_bar, progress_window):
    try:
        progress_bar['value'] = 10
        progress_window.update_idletasks()
        df = pd.read_csv(ruta_csv, low_memory=False)
        progress_bar['value'] = 20
        progress_window.update_idletasks()
        a_col = df.columns[0]
        b_col = df.columns[1]
        doc_col = "special_document"
        attach_col = "special_attachments"
        # Aseguramos que la columna de attachments sea tratada como string
        df[attach_col] = df[attach_col].astype(str).str.split('|')
        progress_bar['value'] = 30
        progress_window.update_idletasks()
        df = df.explode(attach_col)
        progress_bar['value'] = 40
        progress_window.update_idletasks()
        df = df[df[attach_col].notna() & (df[attach_col] != "")]
        progress_bar['value'] = 50
        progress_window.update_idletasks()
        final_result = []
        progress_bar['value'] = 60
        progress_window.update_idletasks()
        for item_id, group in df.groupby(a_col):
            special_document = group.iloc[0][doc_col].replace("file:", "")
            final_result.append({a_col: item_id, b_col: group.iloc[0][b_col], 'Imagenes': special_document})
            for attachment in group[attach_col]:
                final_result.append({a_col: item_id, b_col: group.iloc[0][b_col], 'Imagenes': attachment})
        progress_bar['value'] = 70
        progress_window.update_idletasks()
        final_result_df = pd.DataFrame(final_result)
        # La eliminación de las últimas dos filas se mantiene según la lógica original.
        final_result_df = final_result_df.iloc[:-2]
        final_result_df = final_result_df[[a_col, b_col, 'Imagenes']]
        progress_bar['value'] = 80
        progress_window.update_idletasks()
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Guardar archivo CSV")
        progress_bar['value'] = 90
        progress_window.update_idletasks()
        final_result_df.to_csv(save_path, index=False)
        progress_bar['value'] = 100
        progress_window.update_idletasks()
        progress_window.destroy()
        messagebox.showinfo("Éxito", f"El resultado ha sido guardado en:\n'{save_path}'")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")
        progress_window.destroy()

def progreso_proceso_despipe(ruta_csv):
    prog_window = tk.Toplevel(root)
    prog_window.title("Procesando datos...")
    window_width = 400
    window_height = 150
    screen_width = prog_window.winfo_screenwidth()
    screen_height = prog_window.winfo_screenheight()
    pos_top = int(screen_height/2 - window_height/2)
    pos_right = int(screen_width/2 - window_width/2)
    prog_window.geometry(f"{window_width}x{window_height}+{pos_right}+{pos_top}")
    style = ttk.Style(prog_window)
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor='black', background='orange', thickness=30)
    progress_bar = ttk.Progressbar(prog_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)
    label_text = tk.Label(prog_window, text="Espere mientras se procesan los datos.", font=("Arial", 11))
    label_text.pack(pady=10)
    prog_window.attributes('-topmost', True)
    prog_window.update()
    threading.Thread(target=despipepizar, args=(ruta_csv, progress_bar, prog_window)).start()

def run_despipepizar():
    messagebox.showinfo("Información", "Seleccione el archivo CSV que descargó de TAINACAN.")
    ruta_csv = filedialog.askopenfilename(title="Selecciona CSV", filetypes=[("CSV files", "*.csv")])
    if ruta_csv:
        progreso_proceso_despipe(ruta_csv)
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")

# ============================================
# Funciones de ejemplo (solo prints por ahora)
# ============================================
def run_normalizar_extensiones():
    print("Ejecutando: Normalizar Extensiones")

def run_listar_imagenes():
    print("Ejecutando: Listar Archivos")

def run_renombrar_archivos():
    print("Ejecutando: Renombrar Archivos")

def run_validar_urls():
    print("Ejecutando: Validar URL")

def run_concatenar_filas():
    print("Ejecutando: Concatenar Filas")

def run_despipepizar():
    print("Ejecutando: Despipepizar")

def run_creditos():
    pass  # No usamos esta función para mostrar créditos

# ============================================
# Pantalla de carga
# ============================================
def splash_screen():
    global root
    root = tk.Tk()
    root.withdraw()

    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("500x400+400+200")
    splash.configure(bg="white")

    image = Image.open("secretaria_cultura.png")
    image = image.resize((300, 200), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(image)

    label = tk.Label(splash, image=logo, bg="white")
    label.image = logo
    label.pack(pady=20)

    progress = ttk.Progressbar(splash, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)

    def close_splash():
        splash.destroy()
        root.deiconify()
        main_menu()

    def animate(i=0):
        if i < 100:
            progress["value"] = i
            splash.after(50, animate, i + 5)
        else:
            close_splash()

    animate()
    root.mainloop()

# ============================================
# Interfaz principal con pestañas ajustables
# ============================================
def main_menu():
    global root
    root.title("Procesador CSV Tainacan")
    root.geometry("900x600")
    root.configure(bg="#FFFFFF")
    root.minsize(700, 500)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    # === Frame superior que ocupará todo el ancho ===
    top_frame = tk.Frame(root, bg="#FFFFFF", height=60)
    top_frame.grid(row=0, column=0, sticky="ew")
    top_frame.grid_propagate(False)

    # Logo (posición fija a la izquierda)
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((200, 50), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(top_frame, image=logo_photo, bg="#FFFFFF")
    logo_label.image = logo_photo
    logo_label.place(x=10, y=5)

    # Título (centrado horizontalmente)
    title_label = tk.Label(top_frame, text="Procesador CSV para Repositorio Digital",
                           font=("Helvetica", 14, "bold"), bg="#FFFFFF", fg="black")
    title_label.place(relx=0.5, rely=0.5, anchor="center")

    # === Notebook ===
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    style = ttk.Style()
    style.theme_use('default')
    style.configure('TNotebook.Tab', background='white', foreground='black', padding=(10, 5))
    style.map("TNotebook.Tab",
              background=[("selected", "#8B0000")],
              foreground=[("selected", "black")])

    # Descripciones para cada pestaña
    descripcion_textos = {
        "Extensiones minúsculas": (
            "Esta función normaliza las extensiones de los archivos, "
            "convirtiéndolas a minúsculas para asegurar consistencia."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Listar archivos": (
            "Esta función permite listar todos los archivos disponibles "
            "en el directorio seleccionado."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Renombrar archivos": (
            "Esta función renombra archivos siguiendo un patrón definido "
            "por el usuario."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Validar URL": (
            "Esta función valida que las URLs contenidas en el archivo "
            "sean accesibles y correctas."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Concatenar filas": (
            "Esta función concatena varias filas del archivo CSV "
            "según criterios especificados."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Despipepizar": (
            "Esta función realiza la operación de 'despipepizar', "
            "que consiste en procesar ciertos datos específicos."
            "\n\n(Agrega aquí más detalles de cómo funciona esta función)"
        ),
        "Créditos": (
            "Omar es el encargado del código fuente así como también de la versión de Windows.\n\n"
            "Axel Cerecedo es encargado de la versión de Windows."
        )
    }

    # Crear las pestañas con sus textos
    for nombre, funcion in descripcion_textos.items():
        frame = ttk.Frame(notebook)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        notebook.add(frame, text=nombre)

        inner_frame = tk.Frame(frame, bg="white", padx=20, pady=20)
        inner_frame.grid(row=0, column=0, sticky="nsew")

        border_frame = tk.Frame(inner_frame, bg="#F0F0F0", bd=2, relief="groove")
        border_frame.pack(expand=True, fill="both", padx=30, pady=30)

        titulo = tk.Label(border_frame, text=nombre, font=("Georgia", 18, "bold"), bg="#F0F0F0", fg="#8B0000")
        titulo.pack(pady=(20, 10))

        contenido = tk.Label(border_frame, text=descripcion_textos[nombre], font=("Helvetica", 14),
                             bg="#F0F0F0", justify="left")
        contenido.pack(padx=20, pady=(0,20), anchor="w")

    # Botón salir
    boton_salir = tk.Button(root, text="Salir", command=root.quit,
                            bg="white", fg="black", font=("Arial", 10, "bold"),
                            width=20, height=2)
    boton_salir.grid(row=2, column=0, pady=10)
    boton_salir.bind("<Enter>", lambda e: boton_salir.configure(bg="#000000", fg="black"))
    boton_salir.bind("<Leave>", lambda e: boton_salir.configure(bg="black", fg="black"))

if __name__ == "__main__":
    splash_screen()

    #NWKIT
    #NWJS

    