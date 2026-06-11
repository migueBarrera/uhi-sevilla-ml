import os
from botocore.exceptions import ClientError
import boto3

def get_s3_client(config):
    """
    Inicializa y devuelve el cliente de boto3 usando la AppConfig.
    """
    return boto3.client(
        's3',
        aws_access_key_id=config.aws_access_key,
        aws_secret_access_key=config.aws_secret_key,
        aws_session_token=config.aws_session_token,
        region_name=config.aws_region
    )

def setup_bucket(s3_client, bucket_name: str, region: str) -> None:
    """
    Comprueba si el bucket existe y si tienes acceso. Si no, lo crea.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ El bucket '{bucket_name}' ya existe y está listo para usarse.")
        
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        
        if error_code == 404:
            print(f"⚙️ El bucket '{bucket_name}' no existe. Procediendo a crearlo...")
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ Bucket '{bucket_name}' creado con éxito.")
            except ClientError as e_create:
                print(f"❌ Error al intentar crear el bucket: {e_create}")
        
        elif error_code == 403:
            print(f"❌ Error: El nombre '{bucket_name}' ya está en uso por otro usuario de AWS.")
        else:
            print(f"❌ Error inesperado al verificar el bucket: {e}")

def upload_data_to_s3(s3_client, file_path: str, bucket_name: str, object_name: str = None) -> None:
    """
    Sube un archivo local al bucket de S3.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)
        
    try:
        print(f"⏳ Subiendo '{file_path}' a 's3://{bucket_name}/{object_name}'...")
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"✅ Subida completada con éxito.")
    except ClientError as e:
        print(f"❌ Error al subir el archivo: {e}")
    except FileNotFoundError:
        print(f"❌ Error: No se ha encontrado el archivo local '{file_path}'.")


def download_data_from_s3(s3_client, bucket_name: str, object_name: str, local_file_path: str) -> None:
    """
    Descarga un archivo de un bucket de S3 a una ruta local.
    """
    local_dir = os.path.dirname(local_file_path)
    if local_dir:
        os.makedirs(local_dir, exist_ok=True)

    try:
        print(f"⏳ Descargando 's3://{bucket_name}/{object_name}' en '{local_file_path}'...")
        s3_client.download_file(bucket_name, object_name, local_file_path)
        print("✅ Descarga completada con éxito.")
    except ClientError as e:
        print(f"❌ Error al descargar el archivo: {e}")