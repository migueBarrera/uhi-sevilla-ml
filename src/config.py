import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class AppConfig:
    aws_access_key: str
    aws_secret_key: str
    aws_session_token: str
    aws_region: str
    s3_bucket_name: str
    mongo_uri: str
    db_name: str
    collection_name: str
    gee_project: str


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_key=os.getenv("AWS_SECRET_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        aws_region=os.getenv("AWS_REGION"),
        s3_bucket_name=os.getenv("S3_BUCKET_NAME"),
        mongo_uri=os.getenv("MONGO_URI"),
        db_name=os.getenv("DB_NAME"),
        collection_name=os.getenv("COLLECTION_NAME"),
        gee_project=os.getenv("GEE_PROJECT"),
    )
