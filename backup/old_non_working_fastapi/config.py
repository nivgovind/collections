import os
from dotenv import load_dotenv



load_dotenv()


class Config:
    AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION=os.getenv('AWS_REGION')
    S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')
    NVIDIA_API_KEY=os.getenv('NVIDIA_API_KEY')
    
fastapi_config = Config()