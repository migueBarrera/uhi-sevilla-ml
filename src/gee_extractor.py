import ee
import requests


def descargar_datos_sevilla(
    gee_project,
    fecha_inicio='2025-07-01',
    fecha_fin='2025-08-31',
    output_path='sevilla_dataset.tif'
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
    return output_path
