import os
import boto3
import pymongo
import rasterio
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from gee_extractor import descargar_datos_sevilla

# Cargar variables de entorno desde .env
load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

GEE_PROJECT = os.getenv('GEE_PROJECT')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# ==========================================
# FASE 1: DESPLIEGUE DE ARQUITECTURA
# ==========================================
print("🚀 FASE 1: Desplegando Arquitectura Cloud...")

# 1.1 Desplegar Bucket en S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)

try:
    if AWS_REGION == 'us-east-1':
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
    else:
        s3_client.create_bucket(
            Bucket=S3_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
        )
    print(f"✅ Bucket S3 '{S3_BUCKET_NAME}' creado/verificado.")
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f"✅ Bucket S3 '{S3_BUCKET_NAME}' ya existe y está listo.")
    else:
        print(f"❌ Error en S3: {e}")

# 1.2 Desplegar Base de Datos en MongoDB Atlas e Índices
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# Limpiamos la colección para que el script sea idempotente (reiniciable)
collection.delete_many({})

# Crear índice geoespacial 2dsphere para consultas de alta velocidad en el simulador
collection.create_index([("location", pymongo.GEOSPHERE)])
print(f"✅ MongoDB configurado. Índice '2dsphere' creado en la colección '{COLLECTION_NAME}'.")


# ==========================================
# FASE 1.5: GENERACIÓN DE DATOS DESDE GOOGLE EARTH ENGINE
# ==========================================
print("\n🛰️ FASE 1.5: Generando datos desde Google Earth Engine...")
ARCHIVO_LOCAL_TIFF = descargar_datos_sevilla(gee_project=GEE_PROJECT)

# ==========================================
# FASE 2: INGESTA DE DATOS
# ==========================================
print("\n📥 FASE 2: Ingesta de Datos (Data Lake)...")
# Subimos el archivo raw a S3 para preservar la fuente de verdad original
s3_key = 'landsat_sentinel_sevilla_raw.tif'
s3_client.upload_file(ARCHIVO_LOCAL_TIFF, S3_BUCKET_NAME, s3_key)
print(f"✅ Archivo raw subido a s3://{S3_BUCKET_NAME}/{s3_key}")


# ==========================================
# FASE 3: PROCESAMIENTO Y TRANSFORMACIÓN (ETL)
# ==========================================
print("\n⚙️ FASE 3: Procesando Información (Ráster a Tabular)...")

with rasterio.open(ARCHIVO_LOCAL_TIFF) as src:
    ndvi_arr = src.read(1)
    ndbi_arr = src.read(2)
    lst_arr = src.read(3)
    
    filas, columnas = ndvi_arr.shape
    cols_grid, rows_grid = np.meshgrid(np.arange(columnas), np.arange(filas))
    longitudes, latitudes = rasterio.transform.xy(src.transform, rows_grid, cols_grid)

# --- INGENIERÍA DE CARACTERÍSTICAS: Calcular Variable Relativa (Distance to Water) ---
# Identificamos el agua (Río Guadalquivir) donde el NDVI y el NDBI son negativos
mascara_agua = (ndvi_arr < 0) & (ndbi_arr < 0)
tierra_array = ~mascara_agua

# Calculamos la distancia euclídea al agua más cercana (cada píxel son 10 metros)
distancia_agua_metros = distance_transform_edt(tierra_array) * 10

# Aplanamos las matrices
df = pd.DataFrame({
    'Longitude': np.array(longitudes).flatten(),
    'Latitude': np.array(latitudes).flatten(),
    'NDVI': ndvi_arr.flatten(),
    'NDBI': ndbi_arr.flatten(),
    'D2W_meters': distancia_agua_metros.flatten(),
    'LST_Target': lst_arr.flatten()
})

# Limpieza y eliminación de valores nulos fuera de la máscara
df_clean = df.dropna().copy()
print(f"✅ Procesamiento ETL finalizado. {len(df_clean)} píxeles listos para base de datos.")


# ==========================================
# FASE 4: UNIFICACIÓN (CARGA EN REPOSITORIO ÚNICO)
# ==========================================
print("\n📤 FASE 4: Unificación en Repositorio Único (MongoDB Atlas)...")

# Convertimos el DataFrame a un formato de diccionarios con estándar GeoJSON
documentos_mongo = []
for index, row in df_clean.iterrows():
    # Estructura de documento optimizada para Machine Learning espacial
    doc = {
        "location": {
            "type": "Point",
            "coordinates": [row['Longitude'], row['Latitude']] # Formato estricto GeoJSON [Lon, Lat]
        },
        "features": {
            "NDVI": float(row['NDVI']),
            "NDBI": float(row['NDBI']),
            "Distance_to_Water_m": float(row['D2W_meters'])
        },
        "target": {
            "LST_Celsius": float(row['LST_Target'])
        }
    }
    documentos_mongo.append(doc)

# Inserción masiva optimizada por lotes (Batch Insert)
BATCH_SIZE = 10000
for i in range(0, len(documentos_mongo), BATCH_SIZE):
    batch = documentos_mongo[i:i + BATCH_SIZE]
    collection.insert_many(batch)
    print(f"  -> Insertados {i + len(batch)} de {len(documentos_mongo)} documentos...")

print(f"\n🎉 ¡Hito 0 Completado! La arquitectura está desplegada y los datos integrados.")