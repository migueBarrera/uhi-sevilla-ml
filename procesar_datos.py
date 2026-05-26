import os
import shutil
import argparse

try:
    from src.cloud import setup_mongo_collection
    from src.config import load_config
    from src.etl import raster_to_dataframe
    from src.mongo_loader import dataframe_to_mongo_documents, insert_documents_in_batches
    from src.output_writer import save_dataframe_to_csv
    from src.spatial_join import unir_datos_espaciales

except ModuleNotFoundError:
    from src.cloud import setup_mongo_collection
    from src.config import load_config
    from src.etl import raster_to_dataframe
    from src.mongo_loader import dataframe_to_mongo_documents, insert_documents_in_batches
    from src.output_writer import save_dataframe_to_csv


def ejecutar_procesamiento(archivo_local_tiff, arbolado_csv, carreteras_csv, edificios_csv):
    config = load_config()

    processed_dir = os.path.join("outputs", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    for ruta in (archivo_local_tiff, arbolado_csv, carreteras_csv, edificios_csv):
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No existe el fichero requerido: {ruta}")

    ARCHIVO_LOCAL_TIFF = archivo_local_tiff

    # collection = setup_mongo_collection(
    #     config.mongo_uri,
    #     config.db_name,
    #     config.collection_name,
    # )

   # ==========================================
    # FASE 3: PROCESAMIENTO Y TRANSFORMACIÓN (ETL)
    # ==========================================
    print("\n⚙️ FASE 3: Procesando Información (Ráster a Tabular)...")

    # 1. Extraemos los datos del satélite
    pixel_data_df = raster_to_dataframe(ARCHIVO_LOCAL_TIFF)
    
    # 2. MATCH ESPACIAL: Unimos con arbolado, carreteras y edificios
    pixel_data_df = unir_datos_espaciales(pixel_data_df, arbolado_csv, carreteras_csv, edificios_csv)

    # 3. Guardamos el DataFrame final enriquecido
    output_csv_path = save_dataframe_to_csv(pixel_data_df, outputs_dir=processed_dir)

    output_tiff_path = os.path.join(processed_dir, os.path.basename(ARCHIVO_LOCAL_TIFF))
    if os.path.abspath(ARCHIVO_LOCAL_TIFF) != os.path.abspath(output_tiff_path):
        shutil.copy2(ARCHIVO_LOCAL_TIFF, output_tiff_path)

    print(f"✅ Procesamiento ETL finalizado. {len(pixel_data_df)} píxeles listos para base de datos.")

    # ==========================================
    # FASE 4: UNIFICACIÓN (CARGA EN REPOSITORIO ÚNICO)
    # ==========================================
    print("\n📤 FASE 4: Unificación en Repositorio Único (MongoDB Atlas)...")

    # documentos_mongo = dataframe_to_mongo_documents(pixel_data_df)
    # insert_documents_in_batches(collection, documentos_mongo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesa los datos a partir de tres ficheros de entrada obligatorios.")
    parser.add_argument("--tiff", required=True, help="Ruta al fichero TIFF de entrada")
    parser.add_argument("--arbolado", required=True, help="Ruta al CSV de arbolado de Sevilla")
    parser.add_argument("--carreteras", required=True, help="Ruta al CSV de carreteras")
    parser.add_argument("--edificios", required=True, help="Ruta al CSV de edificios")
    args = parser.parse_args()

    ejecutar_procesamiento(
        archivo_local_tiff=args.tiff,
        arbolado_csv=args.arbolado,
        carreteras_csv=args.carreteras,
        edificios_csv=args.edificios
    )
