from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from document_processors import load_multimodal_data, load_data_from_directory
from utils import set_environment_variables
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from pydantic import BaseModel
import os

app = FastAPI()

def initialize_settings():
    Settings.embed_model = NVIDIAEmbedding(model="nvidia/nv-embedqa-e5-v5", truncate="END")
    Settings.llm = NVIDIA(model="meta/llama-3.1-70b-instruct")
    Settings.text_splitter = SentenceSplitter(chunk_size=600)

def create_index(documents):
    vector_store = MilvusVectorStore(
            host = "127.0.0.1",
            port = 19530,
            dim = 1024
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(documents, storage_context=storage_context)


#pydantic model for query
class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/process_files/")
async def process_files(files: list[UploadFile]):
    set_environment_variables()
    initialize_settings()
    documents = load_multimodal_data(files)
    index = create_index(documents)
    return JSONResponse(content={"message": "Files processed and index created!"})

@app.post("/process_directory/")
async def process_directory(directory_path: str):
    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path.")
    set_environment_variables()
    initialize_settings()
    documents = load_data_from_directory(directory_path)
    index = create_index(documents)
    return JSONResponse(content={"message": "Directory processed and index created!"})


@app.post("/query")
async def query_index(request: QueryRequest):
    query = request.query
    # Assuming you have a global index or a way to retrieve the index
    response = st.session_state['index'].as_query_engine(similarity_top_k=20, streaming=True).query(query)
    full_response = ""
    for token in response.response_gen:
        full_response += token
    return JSONResponse(content={"response": full_response})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)