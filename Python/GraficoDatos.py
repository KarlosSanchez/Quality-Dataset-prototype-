from io import StringIO
import string
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.cluster import DBSCAN
from wordcloud import WordCloud

def main(file_path):
    try:
        # Lee el archivo CSV

        # Crear un DataFrame a partir del archivo CSV
        df = pd.read_csv(StringIO(file_path))

        df = pd.read_csv(file_path, on_bad_lines='skip')
        print("Archivo CSV leido correctamente.")

        # Explorar las primeras filas del dataset
        print(df.head())

        # Obtener estadisticas descriptivas
        print(df.describe())

        # Obtener informacion del dataset
        print(df.info())

        if len(df.columns) > 2:

            # Seleccionar la columna para el grafico
            columna = df.columns[2]
       
            # Crear un grafico automaticamente sin definir las columnas por nombre
            df[columna].value_counts().plot(kind='bar')
            plt.xlabel(columna)
            plt.ylabel(f'Numero de {columna}')
            plt.title(f'Distribucion de {columna}')
            plt.savefig("wwwroot/images/distribucion.png")
            plt.close()
            print("Imagen distribution.png guardada correctamente")
        else:
            print("**** Error: el dataset no tiene suficientes columnas para generan graficos de distribucion.")
            

        # Total records
        print(f"Records : {df.shape[0]}")
        print(f"Columns : {df.shape[1]}")

        # Verifica si hay columnas no numericas y las elimina para el analisis
        df_numeric = df.select_dtypes(include=[float, int])
        print (f"Valor de df_numeric: {df_numeric}")

         # Convertir el DataFrame a un array de numpy
        datos = df_numeric.to_numpy()

        # Imputar valores faltantes
        imputer = SimpleImputer(strategy='mean')
        scaler = StandardScaler()
        datos = imputer.fit_transform(datos)
        #datos = scaler.fit_transform(datos)

         # Identificar Clusters
        valor_eps = 3  # ASIGNAR_VALOR
        valor_min_samples = 3  # ASIGNAR_VALOR

        clusters = DBSCAN(eps=valor_eps, min_samples=valor_min_samples).fit_predict(datos)

         # Grafica de matplotlib para mostrar los Clusters
        plt.figure(figsize=(5.5, 5.5))
        plt.scatter(datos[:, 0], datos[:, 1], c=clusters, s=100)
        plt.xlabel(df_numeric.columns[0])
        plt.ylabel(df_numeric.columns[1])
        plt.title('Algoritmo utilizado CLUSTER')
        plt.savefig("wwwroot/images/clusters.png")
        plt.clf()
        print("Imagen clusters.png guardada correctamente")

        # Genera graficos si hay mas de 2 columanas con numeros
        if len(df_numeric.columns) >= 2:
            print("Entro en > 2 ")
            # Matriz de correlacion
            plt.figure(figsize=(8, 6))
            sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Matriz de Correlacion')
            plt.savefig("wwwroot/images/correlation_matrix.png")
            plt.close()
            print("Imagen correlation_matrix.png guardada correctamente")

            # Pares de graficos (pairplot)
            pairplot_fig = sns.pairplot(df_numeric, diag_kind='kde', aspect=1.5, dropna=True)
            # Ottieni la figura corrente e imposta il titolo 
            pairplot_fig.fig.suptitle('Pairplot de graficos KDE (Kernel Density Estimation)', y=1.02)
            pairplot_fig.savefig("wwwroot/images/pairplot.png")
            plt.close()
            print("Imagen pairplot.png guardada correctamente")
        else:
            print("**** El DataFrame tiene 1 o menos columnas numericas, se generan nubes de palabras.")
            # Concatenar el contenido de las columnas de texto
            text = ' '.join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))
            # Generar la nube de palabras
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            # Mostrar la imagen generada
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.savefig("wwwroot/images/wordcloud.png")
            plt.close()
            print("Imagen wordcloud.png guardada correctamente")

        print("Le grafiche sono state salvate nella cartella 'wwwroot/images/'.")
    except pd.errors.ParserError as e:
        print(f"Error al procesar el archivo CSV: {e}")
    except Exception as e:
        print(f"Ocurrio un error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <file_path>")
    else:
        main(sys.argv[1])
