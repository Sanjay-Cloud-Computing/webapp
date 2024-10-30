import boto3
import os
from botocore.exceptions import NoCredentialsError
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
S3_BUCKET = os.getenv('S3_BUCKET_NAME')

print(S3_BUCKET)

s3_client = boto3.client('s3')

def upload_image_to_s3(file, user_id):
    try:
        file_name = secure_filename(file.filename)
        s3_key = f"{user_id}/{file_name}"
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": file.content_type, "ACL": "private"}
        )
        return f"{S3_BUCKET}/{s3_key}"
    except NoCredentialsError as e:
        print(e)
        raise Exception("S3 Credentials not found")

def delete_image_from_s3(s3_key):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    except NoCredentialsError as e:
        print(e)
        raise Exception("S3 Credentials not found")

