import base64
import uuid
import boto3

from typing import (List)
from app.core.custom_errors import *
from app.core.config import Config_is


class AmazonServices:

    def __init__(self):
        self.s3_client = boto3.client('s3', aws_access_key_id=Config_is.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=Config_is.AWS_SECRET_ACCESS_KEY)
        self.s3_resource = boto3.resource('s3', aws_access_key_id=Config_is.AWS_ACCESS_KEY_ID,
                                          aws_secret_access_key=Config_is.AWS_SECRET_ACCESS_KEY)

    def delete_s3_object(self, path: str) -> bool:
        """
        Delete an object from s3
        """
        self.s3_client.delete_object(Bucket=Config_is.S3_BUCKET_NAME, Key=path)
        return True

    def file_upload_obj_s3(self, new_file_name: str, file_object: object, content_type: str) -> bool:
        """
        Uploads file to s3 bucketS.
        """
        response = self.s3_client.put_object(Bucket=Config_is.S3_BUCKET_NAME, Key=new_file_name, 
                                                ContentType=content_type, Body=file_object.read())
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0) != 200:
            print(response)
            raise InternalError()
        return True
    
    def list_file_objs_s3_folder(self, folder_name: str) -> List:
        """
        Lists all file links in s3 folder.
        """
        response = self.s3_client.list_objects_v2(
            Bucket=Config_is.S3_BUCKET_NAME,
            Prefix=f"{folder_name}/"
        )
        if "Contents" not in response:
            print(f"No files found in folder: {folder_name}/")
            return []
        return [f"https://{Config_is.S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{obj['Key']}" for obj in response["Contents"]]

    def file_encoded_uploader(self, file_is: object, image_type: str, file_path: str) -> bool:
        """
        Upload base64 images to S3 bucket
        """
        s3_obj = self.s3_resource.Object(Config_is.S3_BUCKET_NAME, file_path)
        s3_obj.put(Body=base64.b64decode(file_is), ContentType=image_type, ACL='public-read')
        return True

    def presigned_url(self, file_path: str) -> str:
        r = self.s3_client.generate_presigned_url('get_object', Params={'Bucket': Config_is.S3_BUCKET_NAME, 'Key': file_path})
        return r
    
    def download_s3_object(self, s3_obj_name: str, local_file_path: str) -> bool:
        """
        Download the file from s3 to the specified path.
        Args:
            s3_obj_name: S3 file path
            local_file_path: local file path
        """
        self.s3_client.download_file(Config_is.S3_BUCKET_NAME, s3_obj_name, local_file_path)
        print(f"Downloaded {s3_obj_name} to {local_file_path}")
        return True

