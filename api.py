# from typing import Union
from fastapi import FastAPI, UploadFile, File
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
# import subprocess
from populate_database import populate_database
from query_data import query_rag
from pydantic import BaseModel
class Query(BaseModel):
    query: str

app = FastAPI()
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     # "http://localhost:3000/query",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/query")
async def query(query:Query):
    response_text = query_rag(query)
    return {"response": response_text}


# @app.post("/uploadpdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     with open(os.path.join('data', file.filename), 'wb') as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     await populate_database()
        
#     return {"filename": file.filename}

# @app.get("/files/")
# async def list_files():
#     files = os.listdir('data')
#     return {"files": files}

# @app.delete("/deletepdf/{filename}")
# async def delete_pdf(filename: str):
#     file_path = os.path.join('data', filename)
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         populate_database(reset=True)
#         return {"status": "file deleted"}
#     else:
#         return {"status": "file not found"}

# @app.post("/populate_db_with_clear/")
# async def populate_db_with_clear():
#     populate_database(reset=True)
#     return {"status": "database populated"}

@app.get("/populate_db/")
async def populate_db():
    await populate_database()
    return {"status": "database populated"}