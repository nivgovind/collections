from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.s3_utils import list_buckets, list_documents, upload_file, download_file, check_connection
from config import fastapi_config # contains env variables, access by eg: "fastapi_config.AWS_ACCESS_KEY_ID"
import shutil
import os

from fastapi import FastAPI
from routers import rag

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(rag.router, prefix="/rag", tags=["rag"])

@app.get("/list_buckets")
async def get_buckets():
    buckets = list_buckets()
    return {"buckets": buckets}

@app.get("/list_documents")
async def get_documents():
    objects = list_documents()
    return {"objects": objects}

@app.get("/get_document_details")
def get_document_details(document_name: str):
    try:
        details = get_document_details(document_name)
        return {"details": details}
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))



@app.post("/upload")
async def upload_to_s3(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if upload_file(file.filename, fastapi_config.S3_BUCKET_NAME, file.filename):
            return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Failed to upload file"}, status_code=500)
    finally:
        if os.path.exists(file.filename):
            os.remove(file.filename)
