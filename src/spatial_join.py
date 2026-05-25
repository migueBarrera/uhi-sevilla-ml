import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

def unir_datos_espaciales(pixel_df, ruta_arbolado, ruta_carreteras):
    """
    Cruza el DataFrame de píxeles con los CSVs vectoriales usando distancias espaciales.
    """
    print("🗺️ Realizando el cruce espacial de datos...")
    
    # 1. Cargar los datos tabulares
    df_arboles = pd.read_csv(ruta_arbolado)
    df_carreteras = pd.read_csv(ruta_carreteras)

    # 2. Proyección local a metros (Aproximación para Sevilla)
    # 1 grado de Latitud = ~111320 metros.
    # 1 grado de Longitud en Sevilla (Lat 37.4) = Cos(37.4) * 111320 =~ 88400 metros.
    FACTOR_LON = 88400
    FACTOR_LAT = 111320

    # Convertimos los píxeles principales a metros
    pixels_m = np.column_stack((
        pixel_df['Longitude'].values * FACTOR_LON,
        pixel_df['Latitude'].values * FACTOR_LAT
    ))

    # --- 3. MATCH DE CARRETERAS (Distancia Mínima) ---
    print("  -> 🚗 Calculando distancia a vías principales...")
    carreteras_m = np.column_stack((
        df_carreteras['longitud'].values * FACTOR_LON,
        df_carreteras['latitud'].values * FACTOR_LAT
    ))
    
    # Construimos el índice espacial de carreteras
    tree_carreteras = cKDTree(carreteras_m)
    # 'k=1' busca solo el vecino más cercano
    distancias_carreteras, _ = tree_carreteras.query(pixels_m, k=1)
    pixel_df['D2R_meters'] = distancias_carreteras

    # --- 4. MATCH DE ARBOLADO (Densidad en radio) ---
    print("  -> 🌳 Calculando densidad de arbolado (Radio 50m)...")
    arboles_m = np.column_stack((
        df_arboles['longitud'].values * FACTOR_LON,
        df_arboles['latitud'].values * FACTOR_LAT
    ))
    
    # Construimos el índice espacial de árboles
    tree_arboles = cKDTree(arboles_m)
    # 'r=50' busca todos los puntos en un radio de 50 metros
    indices_arboles = tree_arboles.query_ball_point(pixels_m, r=50)
    
    # Contamos la cantidad de árboles para cada píxel
    pixel_df['Tree_Density_50m'] = [len(idx) for idx in indices_arboles]

    return pixel_df