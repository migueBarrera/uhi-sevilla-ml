import os
import shutil

try:
    from src.config import load_config
    from src.gee_extractor import descargar_datos_sevilla
    from src.arbolado_extractor import descargar_arbolado_csv
    from src.osm_extractor import descargar_carreteras_csv
    from src.osm_buildings import descargar_edificios_csv

except ModuleNotFoundError:
    from src.config import load_config
    from src.gee_extractor import descargar_datos_sevilla
    from src.arbolado_extractor import descargar_arbolado_csv
    from src.osm_extractor import descargar_carreteras_csv


def ejecutar_descarga():
    config = load_config()

    # ==========================================
    # FASE 1.5: GENERACIÓN DE DATOS DESDE GOOGLE EARTH ENGINE
    # ==========================================
    print("\n🛰️ FASE 1.5: Generando datos desde Google Earth Engine y descargando archivo local...")
    #ARCHIVO_LOCAL_TIFF = descargar_datos_sevilla(gee_project=config.gee_project)
    #ARCHIVO_LOCAL_TIFF = "outputs/sevilla_dataset.tif"

    # ==========================================
    # FASE 1.6: DESCARGA DE DATOS COMPLEMENTARIOS (ARBOLADO Y CARRETERAS)
    # ==========================================
    print("\n🌳 FASE 1.6: Descargando datos complementarios...")

    raw_dir = os.path.join("outputs", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    raw_tiff_path = os.path.join(raw_dir, "sevilla_dataset.tif")
    #if os.path.abspath(ARCHIVO_LOCAL_TIFF) != os.path.abspath(raw_tiff_path):
    #    shutil.copy2(ARCHIVO_LOCAL_TIFF, raw_tiff_path)
    print(f"✅ TIFF raw guardado en: {raw_tiff_path}")

    # Descargar inventario de arbolado urbano
    arbolado_csv_path = os.path.join(raw_dir, "arbolado_sevilla.csv")
    #descargar_arbolado_csv(output_file=arbolado_csv_path)

    # Descargar carreteras desde OpenStreetMap
    carreteras_csv_path = os.path.join(raw_dir, "carreteras_sevilla.csv")
    #descargar_carreteras_csv(output_file=carreteras_csv_path)

    # Descargar edificios desde OpenStreetMap
    edificios_csv_path = os.path.join(raw_dir, "edificios_sevilla.csv")
    descargar_edificios_csv(output_file=edificios_csv_path)

    print(f"✅ Datos complementarios descargados en: {raw_dir}/")

    # ==========================================
    # FASE 2: INGESTA DE DATOS
    # ==========================================
    print("\n📥 FASE 2: Ingesta de Datos (Data Lake)...")
    # Subimos el archivo raw a S3 para preservar la fuente de verdad original
    #s3_key = 'landsat_sentinel_sevilla_raw.tif'
    #s3_client.upload_file(ARCHIVO_LOCAL_TIFF, config.s3_bucket_name, s3_key)
    #print(f"✅ Archivo raw subido a s3://{config.s3_bucket_name}/{s3_key}")


if __name__ == "__main__":
    ejecutar_descarga()
