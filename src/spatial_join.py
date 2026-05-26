import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import warnings

def unir_datos_espaciales(pixel_df, ruta_arbolado, ruta_carreteras, ruta_edificios):
    """
    Cruza el DataFrame de píxeles con los CSVs vectoriales usando distancias espaciales.
    """
    print("🗺️ Realizando el cruce espacial de datos...")
    
    # 1. Cargar los datos tabulares
    df_arboles = pd.read_csv(ruta_arbolado)
    df_carreteras = pd.read_csv(ruta_carreteras)
    df_edificios = pd.read_csv(ruta_edificios)

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

    # --- 3. MATCH DE CARRETERAS (Jerarquía de Tráfico) ---
    print("  -> 🚗 Calculando exposición al tráfico por jerarquía...")
    
    # Separamos vías de alta capacidad de vías puramente urbanas
    df_vias_rapidas = df_carreteras[df_carreteras['tipo'].isin(['motorway', 'trunk'])]
    df_vias_urbanas = df_carreteras[~df_carreteras['tipo'].isin(['motorway', 'trunk'])]
    
    # Árbol 1: Vías rápidas (SE-30, autovías)
    rapidas_m = np.column_stack((df_vias_rapidas['longitud'] * FACTOR_LON, df_vias_rapidas['latitud'] * FACTOR_LAT))
    tree_rapidas = cKDTree(rapidas_m)
    dist_rapidas, _ = tree_rapidas.query(pixels_m, k=1)
    pixel_df['D2R_HighCapacity_m'] = dist_rapidas

    # Árbol 2: Vías urbanas (primary, secondary)
    urbanas_m = np.column_stack((df_vias_urbanas['longitud'] * FACTOR_LON, df_vias_urbanas['latitud'] * FACTOR_LAT))
    tree_urbanas = cKDTree(urbanas_m)
    dist_urbanas, _ = tree_urbanas.query(pixels_m, k=1)
    pixel_df['D2R_Urban_m'] = dist_urbanas

    # --- 4. MATCH DE ARBOLADO (Densidad en 50m) ---
    print("  -> 🌳 Calculando densidad de biomasa (Radio 50m)...")
    arboles_m = np.column_stack((df_arboles['longitud'] * FACTOR_LON, df_arboles['latitud'] * FACTOR_LAT))
    tree_arboles = cKDTree(arboles_m)
    indices_arboles = tree_arboles.query_ball_point(pixels_m, r=50)
    pixel_df['Tree_Density_50m'] = [len(idx) for idx in indices_arboles]

    # --- 5. MATCH DE EDIFICIOS (Morfología y Proxy SVF en 100m) ---
    print("  -> 🏢 Calculando morfología urbana y Sky View Factor (Radio 100m)...")
    edificios_m = np.column_stack((df_edificios['longitud'] * FACTOR_LON, df_edificios['latitud'] * FACTOR_LAT))
    tree_edificios = cKDTree(edificios_m)
    
    # Buscamos todos los edificios en un radio de 100 metros del píxel
    indices_edificios = tree_edificios.query_ball_point(pixels_m, r=100)
    alturas_array = df_edificios['altura_estimada'].values
    
    # Cálculos vectorizados para evitar bucles lentos
    # 1. Cantidad de edificios (Densidad constructiva)
    pixel_df['Building_Density_100m'] = [len(idx) for idx in indices_edificios]
    
    # 2. Altura media (Si no hay edificios, la altura es 0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # np.mean lanza warning si la lista está vacía, lo capturamos e inyectamos 0
        pixel_df['Avg_Building_Height_100m'] = [
            np.mean(alturas_array[idx]) if len(idx) > 0 else 0.0 
            for idx in indices_edificios
        ]

    return pixel_df