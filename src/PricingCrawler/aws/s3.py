from typing import Any
import boto3


class S3_Client:
    s3: Any
    bucket_name: str
    subdir: str

    def __init__(self, s3_bucketname, s3_subdir) -> None:
        self.s3 = boto3.client("s3")
        self.bucket_name = s3_bucketname
        self.subdir = s3_subdir

    def create_multipart_upload(self, file_name: str):
        return self.s3.create_multipart_upload(
            Bucket=self.bucket_name, Key=self.subdir + file_name
        )

    def upload_part(
        self,
        file_name: str,
        part_number: int,
        upload_id: int,
        buffer,
    ):
        return self.s3.upload_part(
            Bucket=self.bucket_name,
            Key=self.subdir + file_name,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=buffer,
        )

    def complete_multipart_upload(self, file_name: str, upload_id: str, parts):
        return self.s3.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.subdir + file_name,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )
