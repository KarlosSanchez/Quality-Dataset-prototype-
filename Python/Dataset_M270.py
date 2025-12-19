#Prototipo dataset TT Sanchez 2025
#Version  M_270
import pandas as pd
import os
import json
import timeit
import itertools
import csv
import codecs
import re
import timeit
from tkinter import filedialog
from tkinter import Tk
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)


# Definir el patrón de expresiones regulares para múltiples formatos de fecha
patron = re.compile(
    r'^\d{2}[/.]\d{2}[/.]\d{4}$|'  # Formato DD/MM/AAAA o DD.MM.AAAA 
    r'^\d{4}-\d{2}-\d{2}$|'        # Formato AAAA-MM-DD 
    r'^\d{2}/\d{2}/\d{4}$|'        # Formato MM/DD/AAAA 
    r'^\d{2}-\d{2}-\d{4}$|'        # Formato DD-MM-AAAA 
    r'^\d{2} \d{2} \d{4}$|'        # Formato DD MM AAAA 
    r'^\d{2}-[A-Za-z]{3}-\d{4}$|'  # Formato DD-MMM-AAAA 
    r'^\d{2} [A-Za-z]+ \d{4}$|'    # Formato DD Month AAAA 
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'  # Formato ISO 8601
)

def verificar_formato_fecha(valor):
    # Verificar si el valor coincide con el patrón de expresiones regulares
    if patron.match(valor):
        return True
    return False

def es_formato_fecha_alternativo(valor):
    # Aquí puedes agregar lógica para verificar otros formatos de fecha
    try:
        datetime.strptime(valor, '%d-%m-%Y')
        return True
    except ValueError:
        return False

def es_numero_max_8_digitos(valor): 
    return valor.isdigit() and len(valor) <= 8

def LlamaFile():
    
    # Crear una ventana emergente para seleccionar el archivo
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    file_path = filedialog.askopenfilename()

    if not file_path:
        print('Nessun file selezionato')
        return
    
    # Convierte file_path en una ruta absoluta
    file_path = os.path.abspath(file_path)

    # Verificar si el archivo existe
    if os.path.isfile(file_path):
        print(f"\n\nRecuperando dataset  : {os.path.basename(file_path)}")
    else:
        print("****Error: El archivo no se puede recuperar. Path error *****")
        return

    # Ruta del archivo
    directorio = os.path.dirname(file_path)
    
    # Obtener el nombre del archivo 
    nombre_archivo = os.path.basename(file_path)
    
    # Nombre de la carpetas de logs Quality_Dataset
    nombre_carpeta_log = 'Logs'
    nombre_carpeta_QualityDataset = 'Quality_Dataset'
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Fecha actual en formato de cadena

    # Definir nombres de archivos según el tipo de archivo 
    if file_path.endswith('.csv'):
        nombre_archivo_errores = f'errores_{fecha_actual}_{nombre_archivo}' 
        nombre_archivo_QualityDataset = f'QualityDataset_{fecha_actual}_{nombre_archivo}' 
    elif file_path.endswith('.xlsx'): 
        nombre_archivo_errores = f'errores_{nombre_archivo}_{fecha_actual}.txt' 
        nombre_archivo_QualityDataset = f'QualityDataset_{nombre_archivo}_{fecha_actual}.xlsx' 
    elif file_path.endswith('.txt'): 
        nombre_archivo_errores = f'errores_{fecha_actual}_{nombre_archivo}' 
        nombre_archivo_QualityDataset = f'QualityDataset_{fecha_actual}_{nombre_archivo}' 
    elif file_path.endswith('.json'): 
        nombre_archivo_errores = f'errores_{nombre_archivo}_{fecha_actual}.json' 
        nombre_archivo_QualityDataset = f'QualityDataset_{nombre_archivo}_{fecha_actual}.json'
    else: raise ValueError("Formato de archivo no soportado. Por favor, use un archivo CSV, Excel, TXT o JSON.") 
    
    # Crear rutas para los archivos de errores y sin errores 
    ruta_carpeta_logs = os.path.join(directorio, nombre_carpeta_log) 
    os.makedirs(ruta_carpeta_logs, exist_ok=True) 
    ruta_archivo_errores = os.path.join(ruta_carpeta_logs, nombre_archivo_errores) 

    ruta_carpeta_Quality = os.path.join(directorio, nombre_carpeta_QualityDataset) 
    os.makedirs(ruta_carpeta_Quality, exist_ok=True) 
    ruta_archivo_sin_errores = os.path.join(ruta_carpeta_Quality, nombre_archivo_QualityDataset)
    
    # Inicio del temporizador
    start_time = timeit.default_timer()
    #print(f"Inicio prototipo :{start_time}")
    
    # Obtiene la fecha y hora actual
    current_time = datetime.now()

    # Imprime la fecha y hora actual y el tiempo de inicio del temporizador
    print(f"Inicio del prototipo : {current_time.strftime('%Y-%m-%d %H:%M:%S')} ")
    
    contador_errores = 0
    dictionary = {}
    data_sin_errores = []


# Código principal
    #FIle CSV/txt
    if file_path.endswith('.csv') or file_path.endswith('.txt'):
    
        with codecs.open(file_path, 'r', encoding='utf-8') as file, codecs.open(ruta_archivo_errores, 'w', encoding='utf-8') as file_errores:
            #Lee la primera linea para detectar delimitador
            first_line = file.readline().strip()
            delimiter = ',' if first_line.count(',') > first_line.count(';') else ';'
            #print (f"Delimitador =  {delimiter}")
        
            # Volver al inicio del file
            file.seek(0)
            
            reader = csv.reader(file, delimiter=delimiter)
    
            # Leer la primera línea para obtener los encabezados
            headers = next(reader)
    
            # Contar el total de columnas 
            total_columnas = len(headers)
            #print(f"Numero de columnas detectadas: {total_columnas}")
            #total_filas = sum(1 for row in reader)  # Contar las filas restantes
            #total_filas -= 1  # Restar 1 para excluir la fila de headers
            #print(f"Numero de filas   : {total_filas}")
            print("Prototipo en progress...")
            
            
            lineas_vistas = {}
            data_sin_errores = []
            total_registros = 0
            contador_errores_completitud = 0
            contador_errores_unicidad = 0
            contador_errores_total = 0
            contador_errores_coherencia = 0

            for i, parts in enumerate(reader, start=2):  # Inicia a contar desde 2 porque la primera línea contiene los encabezados
                total_registros += 1
                if not any(parts):
                    file_errores.write(f"Línea {i}: Error de completitud\n")
                    contador_errores_completitud += 1
                    contador_errores_total += 1
                    continue
                if tuple(parts) in lineas_vistas:
                    file_errores.write(f"Línea {i}: Error de unicidad\n")  # Duplicados
                    contador_errores_unicidad += 1
                    contador_errores_total += 1
                    continue
                
                if len(parts) != len(headers):
                    file_errores.write(f"Línea {i}: Error de coherencia {','.join(parts)}\n")
                    #file_errores.write(f"Longitud de la línea: {len(parts)}, Longitud de los encabezados: {len(headers)}\n")
                    contador_errores_coherencia += 1
                    contador_errores_total += 1
                else:
                    if tuple(parts) not in lineas_vistas:
                        data_sin_errores.append(parts)
                        lineas_vistas[tuple(parts)] = i

                # Verifica formato fecha en cada columna
                for j, valor in enumerate(parts):
                    if valor == "" and valor != "0":
                        file_errores.write(f"Línea {i}, columna '{headers[j]}': Error de Coherencia (valor vacío)\n")
                        contador_errores_total += 1
                        contador_errores_coherencia += 1
                        print(f"Contados errores de coherencia: {contador_errores_coherencia}")
                    elif "000" in valor:
                        continue
                    elif es_numero_max_8_digitos(valor):
                        continue
                    elif verificar_formato_fecha(valor):
                        continue
                    elif not verificar_formato_fecha(valor) and not es_formato_fecha_alternativo(valor):
                        continue
                    #file_errores.write(f"Línea {i}, columna '{headers[j]}': Error de Coherencia ({valor})\n")
                    #contador_errores_total += 1
                    #contador_errores_coherencia += 1
                    print(f"Contados errores de coherencia: {contador_errores_coherencia}")
            
            file_errores.write(f"\nArchivo: {file_path}\n")
            file_errores.write(f"Total Errores de Unicidad: {contador_errores_unicidad}\n")
            file_errores.write(f"Total Errores de Completitud: {contador_errores_completitud}\n")
            file_errores.write(f"Total Errores de Coherencia: {contador_errores_coherencia}\n")
            file_errores.write(f"Total Errores: {contador_errores_total}\n")
            #file_errores.write(f"Columas analizadas : {total_columnas}\n")
            file_errores.write(f"Total registros: {total_registros}")

        # Verificar duplicados en data_sin_errores 
        #data_sin_errores = [list(x) for x in set(tuple(x) for x in data_sin_errores)]
        data_sin_errores.sort(key=lambda x: lineas_vistas[tuple(x)])
    
        df = pd.DataFrame(data_sin_errores, columns=headers)
        if file_path.endswith('.csv'):
            df.to_csv(ruta_archivo_sin_errores, sep=',', index=False, header=True, quoting=csv.QUOTE_NONE, escapechar='\\')
        else:
            with codecs.open(ruta_archivo_sin_errores, 'w', encoding='utf-8') as file_sin_errores:
                file_sin_errores.write(','.join(headers)+ '\n')
                for row in data_sin_errores:
                    file_sin_errores.write(','.join(row)+ '\n')
    
    #EXCEL
    elif file_path.endswith('.xlsx'): 
        df = pd.read_excel(file_path) 
        lineas_vistas = set() 
        data_sin_errores = [] 
        contador_errores_total = contador_errores_completitud = contador_errores_unicidad = contador_errores_coherencia = contador_errores_estructura = total_registros = 0 
        
        with open(ruta_archivo_errores, 'w') as file_errores: 
            for i, row in df.iterrows(): 
                total_registros +=1
                # Verificar si la fila está completamente vacía 
                if row.isnull().all(): 
                    print(f"Error en linea {i + 2}: Error de completitud") 
                    file_errores.write(f"Linea {i + 2}: Error de completitud\n") 
                    contador_errores_completitud += 1
                    contador_errores_total += 1
                    continue 
                elif row.isnull().any(): 
                    print(f"Error en linea {i + 2}: {row}") 
                    #file_errores.write(f"\nError en Línea {i + 2}: {row}\n")
                    file_errores.write(f"Error en Linea {i + 2}: Error estructura/columna\n {row.values} \n") 
                    contador_errores_estructura += 1
                    contador_errores_total += 1 
                else: 
                    # Convertir la fila a una tupla para verificar duplicados 
                    row_tuple = tuple(row) 
                    if row_tuple in lineas_vistas: 
                        print(f"Error en linea {i + 2}: Error de Unicidad") 
                        file_errores.write(f"Error en Linea {i + 2}: Error de unicidad\n {row.values}") 
                        contador_errores_unicidad += 1
                        contador_errores_total += 1 
                    else: 
                        data_sin_errores.append(row) 
                        lineas_vistas.add(row_tuple)
                        
                        # Verificar formato de fecha en cada columna 
                        for j, valor in enumerate(row):
                            #if (df.iloc[:, j](lambda x: isinstance(x,(int, float)) and len(str(int(x)))) <= 14).all(): 
                            if df.iloc[:, j].apply(lambda x: isinstance(x, (int, float)) and len(str(int(x))) <= 14).all():

                                
                                if not pd.api.types.is_datetime64_any_dtype(df.iloc[:, j]): 
                                    df.iloc[:, j] = pd.to_datetime(df.iloc[:,j], errors='coerce')

                                if pd.api.types.is_datetime64_any_dtype(df.iloc[:, j]): 
                                
                                    if isinstance(valor, str) and not verificar_formato_fecha(valor):
                                        file_errores.write(f"Linea {i + 2}, columna '{df.columns[j]}': Error de Coherencia ({valor})\n") 
                                        contador_errores_coherencia += 1
                                        contador_errores_total += 1
                                    elif not isinstance(valor, str):
                                        #file_errores.write(f"Linea {i + 2}, columna '{df.columns[j]}': Valor no texto ({valor})\n")  
                                        #contador_errores_total +=1 
                                        continue
                                                
            file_errores.write(f"\n \nArchivo: {file_path}\n")
            file_errores.write(f"Total Errores de Unicidad: {contador_errores_unicidad}\n")
            file_errores.write(f"Total Errores de Completitud: {contador_errores_completitud}\n")
            file_errores.write(f"Total Errores de Coherencia: {contador_errores_coherencia}\n")
            file_errores.write(f"Total Errores de Estructuras: {contador_errores_estructura}\n")
            file_errores.write(f"Total Errores: {contador_errores_total}\n")
            file_errores.write(f"Total registros: {total_registros}")
                        
        df_sin_errores = pd.DataFrame(data_sin_errores)
        df_sin_errores.to_excel(ruta_archivo_sin_errores, index=False)

    elif file_path.endswith('.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
        df = pd.DataFrame(data)
        with open(ruta_archivo_errores, 'w') as file_errores:
            for i, row in df.iterrows():
                # Verificar si la fila está completamente vacía
                if row.isnull().all():
                    print(f"Error en linea {i + 2}: Error de completitud")
                    file_errores.write(f"Linea {i + 2}: Error de completitud\n")
                    contador_errores += 1
                elif row.isnull().any():
                    print(f"Error en linea {i + 2}: {row}")
                    file_errores.write(f"Linea {i + 2}: {row}\n")
                    contador_errores += 1
                else:
                    dictionary[row.iloc[0]] = row.to_dict()
                    data_sin_errores.append(row)
            file_errores.write(f"\nArchivo: {file_path}\n")
            file_errores.write(f"Total de incidencias: {contador_errores}\n")
        df_sin_errores = pd.DataFrame(data_sin_errores)
        df_sin_errores.to_json(ruta_archivo_sin_errores, orient='records', lines=True)

    else:
        raise ValueError("Formato de archivo no soportado. Por favor, use un archivo CSV, Excel, TXT o JSON.")

    print("\n******* Fin Preprocesamiento de datos...")
    print(f"\n******* Numero total de líneas con error   : {contador_errores_total}\n")
    print(f"******* Numero total de records controlados: {total_registros}\n")
    print(f"******* File con errores detectados    : '{ruta_archivo_errores}'")
    print(f"******* File sin errores QualityDataset: '{ruta_archivo_sin_errores}'")
    
    # Fin del temporizador
    end_time = timeit.default_timer()
    execution_time = end_time - start_time

    # Calcula las horas, minutos y segundos
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"\n******* La función se ejecuto en {int(hours)} horas, {int(minutes)} minutos y {seconds:.2f} segundos.\n")
    print("Fin ejecucion Prototipo.\n")







# Prueba la función
try:
    varcols = LlamaFile()
    #print(varcols)
except ValueError as e:
    print(e)
