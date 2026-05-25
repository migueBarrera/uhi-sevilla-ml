import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import distance_transform_edt

def raster_to_dataframe(archivo_local_tiff):
    with rasterio.open(archivo_local_tiff) as src:
        # 1. Variables principales
        ndvi_arr = src.read(1)
        ndbi_arr = src.read(2)
        lst_arr = src.read(3)
        
        # 2. Bandas ópticas para el Albedo (Sentinel-2)
        b2_blue = src.read(4)
        b4_red = src.read(5)
        b8_nir = src.read(6)
        b11_swir1 = src.read(7)
        b12_swir2 = src.read(8)

        filas, columnas = ndvi_arr.shape
        cols_grid, rows_grid = np.meshgrid(np.arange(columnas), np.arange(filas))
        longitudes, latitudes = rasterio.transform.xy(src.transform, rows_grid, cols_grid)

    # Cálculo de la Distancia al Agua
    mascara_agua = (ndvi_arr < 0) & (ndbi_arr < 0)
    tierra_array = ~mascara_agua
    distancia_agua_metros = distance_transform_edt(tierra_array) * 10

    # Cálculo del Albedo de banda ancha
    albedo_arr = (0.356 * b2_blue) + \
                 (0.130 * b4_red) + \
                 (0.373 * b8_nir) + \
                 (0.085 * b11_swir1) + \
                 (0.072 * b12_swir2) - 0.0018
                 
    # Limitamos los valores para que no haya ruido fuera del rango [0, 1]
    albedo_arr = np.clip(albedo_arr, 0, 1)

    # Estructuración final
    df = pd.DataFrame(
        {
            "Longitude": np.array(longitudes).flatten(),
            "Latitude": np.array(latitudes).flatten(),
            "NDVI": ndvi_arr.flatten(),
            "NDBI": ndbi_arr.flatten(),
            "Albedo": albedo_arr.flatten(),
            "D2W_meters": distancia_agua_metros.flatten(),
            "LST_Target": lst_arr.flatten(),
        }
    )
    
    return df.dropna().copy()