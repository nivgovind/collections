import unittest
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
from utils.s3_utils import get_s3_client, list_buckets, list_objects, upload_file, download_file, check_connection
from config import fastapi_config

class TestS3Utils(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key',
            region_name='us-east-1'
        )
        self.s3.create_bucket(Bucket=fastapi_config.S3_BUCKET_NAME)

    @mock_aws
    def test_list_buckets(self):
        response = list_buckets()
        self.assertIn('Buckets', response)
        self.assertEqual(len(response['Buckets']), 1)
        self.assertEqual(response['Buckets'][0]['Name'], fastapi_config.S3_BUCKET_NAME)

    @mock_aws
    def test_list_objects(self):
        self.s3.put_object(Bucket=fastapi_config.S3_BUCKET_NAME, Key='test.txt', Body='test')
        response = list_objects()
        self.assertIn('Contents', response)
        self.assertEqual(len(response['Contents']), 1)
        self.assertEqual(response['Contents'][0]['Key'], 'test.txt')

    @mock_aws
    def test_upload_file(self):
        with patch('s3_utils.get_s3_client', return_value=self.s3):
            response = upload_file('test.txt')
            self.assertIsNone(response)
            objects = self.s3.list_objects_v2(Bucket=fastapi_config.S3_BUCKET_NAME)
            self.assertEqual(len(objects['Contents']), 1)
            self.assertEqual(objects['Contents'][0]['Key'], 'test.txt')

    @mock_aws
    def test_download_file(self):
        self.s3.put_object(Bucket=fastapi_config.S3_BUCKET_NAME, Key='test.txt', Body='test')
        with patch('s3_utils.get_s3_client', return_value=self.s3):
            response = download_file('test.txt', fastapi_config.S3_BUCKET_NAME)
            self.assertIsNone(response)

    @mock_aws
    def test_check_connection(self):
        response = check_connection()
        self.assertIn('Buckets', response)
        self.assertEqual(len(response['Buckets']), 1)
        self.assertEqual(response['Buckets'][0]['Name'], fastapi_config.S3_BUCKET_NAME)

    @mock_aws
    def test_upload_file_client_error(self):
        with patch('s3_utils.get_s3_client', return_value=self.s3):
            with patch('boto3.client.upload_file', side_effect=ClientError({'Error': {'Code': '500'}}, 'upload_file')):
                response = upload_file('non_existent_file.txt')
                self.assertIsInstance(response, ClientError)

    @mock_aws
    def test_download_file_client_error(self):
        with patch('s3_utils.get_s3_client', return_value=self.s3):
            with patch('boto3.client.download_file', side_effect=ClientError({'Error': {'Code': '500'}}, 'download_file')):
                response = download_file('non_existent_file.txt', fastapi_config.S3_BUCKET_NAME)
                self.assertIsInstance(response, ClientError)

if __name__ == '__main__':
    unittest.main()