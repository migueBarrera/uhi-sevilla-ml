try:
    from old.hito1.src.cloud import create_s3_client, ensure_s3_bucket, setup_mongo_collection
    from old.hito1.src.config import load_config
except ModuleNotFoundError:
    from old.hito1.src.cloud import create_s3_client, ensure_s3_bucket, setup_mongo_collection
    from old.hito1.src.config import load_config


def ejecutar_infraestructura():
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


if __name__ == "__main__":
    ejecutar_infraestructura()
