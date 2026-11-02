import os
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'fitcheck-user-assets-dev')


def generate_presigned_put_url(
    key: str,
    content_type: str = 'image/png',
    expires_in: int = 300
) -> str:
    """Generate a presigned URL for uploading to S3."""
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        raise Exception(f"Error generating presigned PUT URL: {e}")


def generate_presigned_get_url(key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for downloading from S3."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': key,
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        raise Exception(f"Error generating presigned GET URL: {e}")


def upload_to_s3(key: str, body: bytes, content_type: str = 'image/png') -> None:
    """Upload data directly to S3."""
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType=content_type
        )
    except ClientError as e:
        raise Exception(f"Error uploading to S3: {e}")


def get_from_s3(key: str) -> bytes:
    """Download data from S3."""
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        return response['Body'].read()
    except ClientError as e:
        raise Exception(f"Error downloading from S3: {e}")
