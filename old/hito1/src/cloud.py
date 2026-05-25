import boto3
import pymongo
from botocore.exceptions import ClientError


def create_s3_client(aws_access_key, aws_secret_key, aws_session_token, aws_region):
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token,
        region_name=aws_region,
    )


def ensure_s3_bucket(s3_client, bucket_name, aws_region):
    try:
        if aws_region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": aws_region},
            )
        print(f"✅ Bucket S3 '{bucket_name}' creado/verificado.")
    except ClientError as error:
        if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print(f"✅ Bucket S3 '{bucket_name}' ya existe y está listo.")
        else:
            print(f"❌ Error en S3: {error}")


def setup_mongo_collection(mongo_uri, db_name, collection_name):
    mongo_client = pymongo.MongoClient(mongo_uri)
    db = mongo_client[db_name]
    collection = db[collection_name]

    # Hacemos el proceso reiniciable y garantizamos índice espacial para consultas.
    collection.delete_many({})
    collection.create_index([("location", pymongo.GEOSPHERE)])

    print(
        f"✅ MongoDB configurado. Índice '2dsphere' creado en la colección '{collection_name}'."
    )
    return collection
