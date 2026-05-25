import os
import shutil

try:
    from old.hito1.src.cloud import create_s3_client, ensure_s3_bucket, setup_mongo_collection
    from old.hito1.src.config import load_config
    from old.hito1.src.etl import raster_to_dataframe
    from old.hito1.src.gee_extractor import descargar_datos_sevilla
    from old.hito1.src.mongo_loader import dataframe_to_mongo_documents, insert_documents_in_batches
    from old.hito1.src.output_writer import save_dataframe_to_csv
    from old.hito1.src.arbolado_extractor import descargar_arbolado_csv
    from old.hito1.src.osm_extractor import descargar_carreteras_csv
except ModuleNotFoundError:
    from old.hito1.src.cloud import create_s3_client, ensure_s3_bucket, setup_mongo_collection
    from old.hito1.src.config import load_config
    from old.hito1.src.etl import raster_to_dataframe
    from old.hito1.src.gee_extractor import descargar_datos_sevilla
    from old.hito1.src.mongo_loader import dataframe_to_mongo_documents, insert_documents_in_batches
    from old.hito1.src.output_writer import save_dataframe_to_csv
    from old.hito1.src.arbolado_extractor import descargar_arbolado_csv
    from old.hito1.src.osm_extractor import descargar_carreteras_csv


config = load_config()

# ==========================================
# FASE 1: DESPLIEGUE DE ARQUITECTURA
# ==========================================
print("🚀 FASE 1: Desplegando Arquitectura Cloud...")

# 1.1 Desplegar Bucket en S3
# s3_client = create_s3_client(
#     config.aws_access_key,
#     config.aws_secret_key,
#     config.aws_session_token,
#     config.aws_region,
# )
#ensure_s3_bucket(s3_client, config.s3_bucket_name, config.aws_region)

# 1.2 Desplegar Base de Datos en MongoDB Atlas e Índices
# collection = setup_mongo_collection(
#     config.mongo_uri,
#     config.db_name,
#     config.collection_name,
# )


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

outputs_dir = "outputs"
os.makedirs(outputs_dir, exist_ok=True)

# Descargar inventario de arbolado urbano
arbolado_csv_path = os.path.join(outputs_dir, "arbolado_sevilla.csv")
descargar_arbolado_csv(output_file=arbolado_csv_path)

# Descargar carreteras desde OpenStreetMap
carreteras_csv_path = os.path.join(outputs_dir, "carreteras_sevilla.csv")
descargar_carreteras_csv(output_file=carreteras_csv_path)

print(f"✅ Datos complementarios descargados en: {outputs_dir}/")

# ==========================================
# FASE 2: INGESTA DE DATOS
# ==========================================
print("\n📥 FASE 2: Ingesta de Datos (Data Lake)...")
# Subimos el archivo raw a S3 para preservar la fuente de verdad original
#s3_key = 'landsat_sentinel_sevilla_raw.tif'
#s3_client.upload_file(ARCHIVO_LOCAL_TIFF, config.s3_bucket_name, s3_key)
#print(f"✅ Archivo raw subido a s3://{config.s3_bucket_name}/{s3_key}")


# ==========================================
# FASE 3: PROCESAMIENTO Y TRANSFORMACIÓN (ETL)
# ==========================================
print("\n⚙️ FASE 3: Procesando Información (Ráster a Tabular)...")

pixel_data_df = raster_to_dataframe(ARCHIVO_LOCAL_TIFF)

output_csv_path = save_dataframe_to_csv(pixel_data_df, outputs_dir=outputs_dir)

output_tiff_path = os.path.join(outputs_dir, os.path.basename(ARCHIVO_LOCAL_TIFF))
if os.path.abspath(ARCHIVO_LOCAL_TIFF) != os.path.abspath(output_tiff_path):
    shutil.copy2(ARCHIVO_LOCAL_TIFF, output_tiff_path)

print(f"✅ Procesamiento ETL finalizado. {len(pixel_data_df)} píxeles listos para base de datos.")
print(f"✅ CSV guardado en: {output_csv_path}")
print(f"✅ TIFF guardado en: {output_tiff_path}")


# ==========================================
# FASE 4: UNIFICACIÓN (CARGA EN REPOSITORIO ÚNICO)
# ==========================================
print("\n📤 FASE 4: Unificación en Repositorio Único (MongoDB Atlas)...")

# documentos_mongo = dataframe_to_mongo_documents(pixel_data_df)
# insert_documents_in_batches(collection, documentos_mongo)

print(f"\n🎉 ¡Hito 0 Completado! La arquitectura está desplegada y los datos integrados.")