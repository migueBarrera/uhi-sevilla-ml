import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.offline as pyo
import plotly.io as pio

def identificar_valores_nulos_y_tipos(df):
    """Muestra información básica: tipos de datos y valores nulos."""
    print("--- Información del Dataset ---")
    print(df.info())
    print("\n--- Valores Nulos por Columna ---")
    print(df.isnull().sum())
    print("\n--- Estadísticas Descriptivas ---")
    display(df.describe(include='all'))

def graficar_distribuciones(df, columnas_numericas=None, columnas_categoricas=None, columnas_ignorar=None):
    """Genera histogramas para variables numéricas y gráficos de barras para categóricas, omitiendo las columnas especificadas."""
    # Aseguramos que sea una lista vacía si no se pasa nada para evitar errores
    if columnas_ignorar is None:
        columnas_ignorar = []

    if columnas_numericas:
        # Filtramos las columnas numéricas
        cols_num_filtradas = [col for col in columnas_numericas if col not in columnas_ignorar]
        for col in cols_num_filtradas:
            plt.figure(figsize=(8, 4))
            sns.histplot(df[col], kde=True, bins=30, color='skyblue')
            plt.title(f'Distribución (Histograma) de {col}')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.show()
            
    if columnas_categoricas:
        # Filtramos las columnas categóricas
        cols_cat_filtradas = [col for col in columnas_categoricas if col not in columnas_ignorar]
        for col in cols_cat_filtradas:
            plt.figure(figsize=(10, 5))
            # Muestra el top 10 si hay muchas categorías
            sns.countplot(y=df[col], order=df[col].value_counts().index[:10])
            plt.title(f'Top 10 Frecuencias de {col}')
            plt.xlabel('Conteo')
            plt.ylabel(col)
            plt.show()

def detectar_anomalias_boxplots(df, columnas_numericas, columnas_ignorar=None):
    """Genera boxplots para identificar valores atípicos (outliers) en columnas numéricas, omitiendo las especificadas."""
    if columnas_ignorar is None:
        columnas_ignorar = []
        
    # Filtramos las columnas
    cols_num_filtradas = [col for col in columnas_numericas if col not in columnas_ignorar]
    
    for col in cols_num_filtradas:
        plt.figure(figsize=(8, 2))
        sns.boxplot(x=df[col], color='lightgreen')
        plt.title(f'Boxplot de {col} (Detección de Outliers)')
        plt.xlabel(col)
        plt.show()

def graficar_dispersion_mapa(df, col_lat='latitud', col_lon='longitud', col_categoria=None):
    """Genera un diagrama de dispersión sobre un mapa interactivo de OpenStreetMap."""

    pyo.init_notebook_mode(connected=True)
    pio.renderers.default = "notebook"
    
    # Comprobar si las columnas existen en el dataframe
    if col_lat not in df.columns or col_lon not in df.columns:
        print(f"Error: No se encontraron las columnas '{col_lat}' y/o '{col_lon}' en el dataset.")
        return

    # Si hay una categoría (como 'especie'), coloreamos los puntos según ella
    if col_categoria and col_categoria in df.columns:
        fig = px.scatter_mapbox(
            df, 
            lat=col_lat, 
            lon=col_lon, 
            color=col_categoria,
            hover_name=col_categoria, # Al pasar el ratón, muestra el nombre de la especie
            zoom=12, 
            height=600
        )
    else:
        # Si no hay categoría, todos los puntos son del mismo color
        fig = px.scatter_mapbox(
            df, 
            lat=col_lat, 
            lon=col_lon,
            zoom=12, 
            height=600
        )
    
    # Configurar el estilo del mapa para usar OpenStreetMap (gratuito)
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":40,"l":0,"b":0},
        title='Mapa de Dispersión Geográfica'
    )
    
    fig.show()

def graficar_mapa_densidad(df):
    """Genera un mapa de calor estático asegurando limpieza y rendimiento."""
    
    spatial_sample = df.sample(n=min(50000, len(df)), random_state=42)

    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Aquí está el cambio: cmap='hot_r' invierte la escala de colores
    scatter = ax.scatter(spatial_sample['Longitude'], spatial_sample['Latitude'],
                        c=spatial_sample['LST_Target'], cmap='hot_r',
                        s=1, alpha=0.6, edgecolors='none')
                        
    ax.set_xlabel('Longitud', fontsize=12)
    ax.set_ylabel('Latitud', fontsize=12)
    ax.set_title('Distribución Espacial de la Temperatura Superficial (LST)',
                fontsize=14, fontweight='bold')
                
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Temperatura (°C)', fontsize=11)
    
    ax.grid(True, alpha=1)
    plt.tight_layout()
    plt.show()

def analisis_correlacion(df):
    """Calcula y visualiza la matriz de correlación para variables numéricas."""
    # Filtrar solo columnas numéricas
    df_numerico = df.select_dtypes(include=[np.number])
    
    # Excluir identificadores si los hay (suele ser ruido en la correlación)
    cols_a_excluir = [col for col in df_numerico.columns if 'id' in col.lower()]
    df_numerico = df_numerico.drop(columns=cols_a_excluir, errors='ignore')
    
    if df_numerico.shape[1] < 2:
        print("No hay suficientes columnas numéricas para analizar la correlación.")
        return
        
    matriz_corr = df_numerico.corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, square=True, linewidths=.5)
    plt.title('Matriz de Correlación')
    plt.show()