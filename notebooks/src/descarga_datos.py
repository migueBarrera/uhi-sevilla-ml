import os
import ee
import requests
import pandas as pd
import re
import time
from src.config import load_config

def descargar_datos_sevilla(
    gee_project,
    output_path,
    fecha_inicio='2025-07-01',
    fecha_fin='2025-08-31',
    
):
    """
    Extrae datos de Sentinel-2 (NDVI, NDBI) y Landsat 8 (LST) de Google Earth Engine
    para el área de Sevilla capital y los descarga como un GeoTIFF multibanda.

    Args:
        gee_project (str): ID del proyecto de Google Earth Engine.
        fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.
        output_path (str): Ruta local donde se guardará el archivo GeoTIFF.

    Returns:
        str: Ruta al archivo GeoTIFF descargado.
    """
    # 1. Autenticación e inicialización en Google Earth Engine
    try:
        ee.Initialize(project=gee_project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=gee_project)

    # 2. Definir el área de interés (Sevilla capital aprox.)
    # Coordenadas: [Longitud Mínima, Latitud Mínima, Longitud Máxima, Latitud Máxima]
    sevilla_bbox = [-6.03, 37.33, -5.90, 37.45]
    aoi = ee.Geometry.Rectangle(sevilla_bbox)

    print("🛰️ Conectando con Earth Engine y filtrando colecciones...")

    # ==========================================
    # 3. EXTRACCIÓN DE SENTINEL-2 (ÓPTICO - 10m)
    # ==========================================
    s2_coleccion = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                    .filterBounds(aoi)
                    .filterDate(fecha_inicio, fecha_fin)
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)))

    s2_img = s2_coleccion.median().clip(aoi)

    # NDVI = (NIR - RED) / (NIR + RED) -> En S2: NIR es B8, RED es B4
    ndvi = s2_img.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # NDBI = (SWIR - NIR) / (SWIR + NIR) -> En S2: SWIR es B11, NIR es B8
    ndbi = s2_img.normalizedDifference(['B11', 'B8']).rename('NDBI')

    # Extraer bandas ópticas y escalarlas a reflectancia (0 a 1)
    # Sentinel-2 SR almacena los valores multiplicados por 10000
    bandas_opticas = s2_img.select(['B2', 'B4', 'B8', 'B11', 'B12']).divide(10000.0)

    # ==========================================
    # 4. EXTRACCIÓN DE LANDSAT 8 (TÉRMICO - 30m)
    # ==========================================
    l8_coleccion = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                    .filterBounds(aoi)
                    .filterDate(fecha_inicio, fecha_fin)
                    .filter(ee.Filter.lt('CLOUD_COVER', 10)))

    l8_img = l8_coleccion.median().clip(aoi)

    # ST_B10 viene escalada: multiplicamos por 0.00341802, sumamos 149.0 (Kelvin) y restamos 273.15 (°C)
    lst_celsius = (l8_img.select('ST_B10')
                   .multiply(0.00341802)
                   .add(149.0)
                   .subtract(273.15)
                   .rename('LST'))

    # ==========================================
    # 5. UNIFICAR BANDAS Y DESCARGAR
    # ==========================================
    dataset_final = (ndvi
                     .addBands(ndbi)
                     .addBands(lst_celsius)
                     .addBands(bandas_opticas.select('B2'))
                     .addBands(bandas_opticas.select('B4'))
                     .addBands(bandas_opticas.select('B8'))
                     .addBands(bandas_opticas.select('B11'))
                     .addBands(bandas_opticas.select('B12')))

    url_descarga = dataset_final.getDownloadURL({
        'scale': 20,          # Remuestreo a 20m (resolución de Sentinel-2)
        'crs': 'EPSG:4326',
        'region': aoi,
        'format': 'GEO_TIFF'
    })

    print("⬇️ Descargando GeoTIFF desde Earth Engine...")
    response = requests.get(url_descarga, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ GeoTIFF descargado correctamente en: {output_path}")


def descargar_arbolado_csv(
    bbox="37.33,-6.03,37.45,-5.90",
    output_file="arbolado_sevilla.csv",
    divisiones_lat=4,
    divisiones_lon=4,
):
    """
    Descarga el arbolado desde OpenStreetMap (Overpass API) y lo guarda en CSV.

    Usa una cuadrícula sobre el bbox para evitar límites de consulta y deduplica
    por ID de OSM para obtener el mayor número posible de árboles del área.
    """
    print("🌳 Descargando arbolado urbano desde OpenStreetMap (Overpass API)...")

    lat_min, lon_min, lat_max, lon_max = [float(v.strip()) for v in bbox.split(",")]

    paso_lat = (lat_max - lat_min) / divisiones_lat
    paso_lon = (lon_max - lon_min) / divisiones_lon

    overpass_url = "https://overpass-api.de/api/interpreter"
    headers = {
        'User-Agent': 'ThermoSevilla_TFM_Project/1.0',
        'Accept': 'application/json',
    }

    arboles = {}
    total_celdas = divisiones_lat * divisiones_lon
    celda_actual = 0

    for i in range(divisiones_lat):
        celda_lat_min = lat_min + i * paso_lat
        celda_lat_max = lat_max if i == divisiones_lat - 1 else lat_min + (i + 1) * paso_lat

        for j in range(divisiones_lon):
            celda_actual += 1
            celda_lon_min = lon_min + j * paso_lon
            celda_lon_max = lon_max if j == divisiones_lon - 1 else lon_min + (j + 1) * paso_lon

            print(f"  · Consultando celda {celda_actual}/{total_celdas}...")

            overpass_query = f"""
            [out:json][timeout:180];
            (
              node["natural"="tree"]({celda_lat_min},{celda_lon_min},{celda_lat_max},{celda_lon_max});
            );
            out body;
            """

            data = None
            for intento in range(3):
                try:
                    response = requests.get(
                        overpass_url,
                        params={'data': overpass_query},
                        headers=headers,
                        timeout=240,
                    )
                    response.raise_for_status()
                    data = response.json()
                    break
                except requests.RequestException:
                    if intento == 2:
                        raise
                    time.sleep(2)

            for element in data.get('elements', []):
                if element.get('type') != 'node':
                    continue

                tags = element.get('tags', {})
                arboles[element['id']] = {
                    'id_arbol': element['id'],
                    'especie': tags.get('species') or tags.get('genus') or tags.get('leaf_type') or 'desconocida',
                    'latitud': element.get('lat'),
                    'longitud': element.get('lon'),
                }

            # Pequeña pausa para no saturar el endpoint público.
            time.sleep(0.3)

    if not arboles:
        raise ValueError("No se encontraron árboles en las coordenadas indicadas.")

    df_arboles = pd.DataFrame(arboles.values()).sort_values('id_arbol')
    df_arboles.to_csv(output_file, index=False, encoding='utf-8')

    print(f"✅ Descarga completada: {output_file} ({len(df_arboles)} árboles registrados)")
    return output_file

def descargar_carreteras_csv(bbox="37.33,-6.03,37.45,-5.90", output_file="carreteras_sevilla.csv"):
    """
    Se conecta a la API de OpenStreetMap, descarga las vías principales
    y las guarda en un archivo CSV.
    """
    print("🚗 Conectando a OpenStreetMap (Overpass API)...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      way["highway"~"motorway|trunk|primary|secondary"]({bbox});
    );
    out center; 
    """
    
    # Añadimos cabeceras para evitar el bloqueo 406 Not Acceptable de Overpass
    headers = {
        'User-Agent': 'ThermoSevilla_TFM_Project/1.0',
        'Accept': 'application/json'
    }
    
    # Pasamos los headers en la petición
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    carreteras_data = []
    
    for element in data['elements']:
        if element['type'] == 'way' and 'center' in element:
            carreteras_data.append({
                'id_via': element['id'],
                'tipo': element['tags'].get('highway', 'desconocido'),
                'nombre': element['tags'].get('name', 'Sin nombre'),
                'latitud': element['center']['lat'],
                'longitud': element['center']['lon']
            })
            
    if not carreteras_data:
        raise ValueError("No se encontraron carreteras en las coordenadas indicadas.")

    # Guardar en CSV
    df_carreteras = pd.DataFrame(carreteras_data)
    df_carreteras.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Descarga completada: {output_file} ({len(df_carreteras)} tramos viales registrados)")
    return output_file

def estimar_altura(tags):
    """
    Intenta extraer la altura en metros. Si no existe, usa el número de plantas.
    Si no hay datos, asume un edificio promedio de 2 plantas (6 metros).
    """
    # 1. Intentar sacar la altura exacta ('height')
    if 'height' in tags:
        try:
            # Limpiamos letras por si alguien escribió "15m" en lugar de "15"
            altura_limpia = re.sub(r'[^\d.]', '', str(tags['height']))
            return float(altura_limpia)
        except ValueError:
            pass
            
    # 2. Intentar sacar las plantas ('building:levels') y multiplicar por 3m/planta
    if 'building:levels' in tags:
        try:
            plantas_limpias = re.sub(r'[^\d.]', '', str(tags['building:levels']))
            return float(plantas_limpias) * 3.0
        except ValueError:
            pass
            
    # 3. Valor por defecto para ciudad (2 plantas)
    return 6.0

def descargar_edificios_csv(bbox="37.33,-6.03,37.45,-5.90", output_file="edificios_sevilla.csv"):
    """
    Se conecta a la API de OpenStreetMap, descarga los polígonos de edificios,
    calcula su centro y estima su altura.
    """
    print("🏢 Conectando a OpenStreetMap para descargar edificios (Esto puede tardar varios minutos)...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Aumentamos el timeout a 900 segundos porque son muchísimos datos
    overpass_query = f"""
    [out:json][timeout:900];
    (
      way["building"]({bbox});
      relation["building"]({bbox});
    );
    out center; 
    """
    
    headers = {
        'User-Agent': 'ThermoSevilla_TFM_Project/1.0',
        'Accept': 'application/json'
    }
    
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    edificios_data = []
    
    for element in data['elements']:
        # Solo guardamos si Overpass pudo calcular el centro geométrico del edificio
        if 'center' in element:
            altura = estimar_altura(element.get('tags', {}))
            
            edificios_data.append({
                'id_edificio': element['id'],
                'latitud': element['center']['lat'],
                'longitud': element['center']['lon'],
                'altura_estimada': altura
            })
            
    if not edificios_data:
        raise ValueError("No se encontraron edificios en las coordenadas indicadas.")

    # Guardar en CSV
    df_edificios = pd.DataFrame(edificios_data)
    df_edificios.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Descarga completada: {output_file} ({len(df_edificios)} edificios registrados)")
    return output_file

def ejecutar_descarga(raw_dir):
    config = load_config()

    print("configuración cargada correctamente." + f" Proyecto GEE: {config.gee_project}")

    sevilla_tif_path = os.path.join(raw_dir, "sevilla_dataset.tif")
    descargar_datos_sevilla(gee_project=config.gee_project, output_path=sevilla_tif_path)

    print("\n Descargando datos complementarios...")

    arbolado_csv_path = os.path.join(raw_dir, "arbolado_sevilla.csv")
    descargar_arbolado_csv(output_file=arbolado_csv_path)

    carreteras_csv_path = os.path.join(raw_dir, "carreteras_sevilla.csv")
    descargar_carreteras_csv(output_file=carreteras_csv_path)

    edificios_csv_path = os.path.join(raw_dir, "edificios_sevilla.csv")
    descargar_edificios_csv(output_file=edificios_csv_path)
     
    print(f" Datos complementarios descargados en: {raw_dir}/")

if __name__ == "__main__":
    path = os.path.join("..", "datasets", "raw")
    ejecutar_descarga(raw_dir=path)
