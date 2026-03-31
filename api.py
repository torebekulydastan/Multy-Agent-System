from fastapi import FastAPI,UploadFile,File,HTTPException
from pydantic import BaseModel
import shutil
from pathlib import Path

from src.rag_engine import RAGEngine

app = FastAPI(title='rag api')

rag = RAGEngine()


UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok = True)

class QureyRequest(BaseModel):
    question:str
    top_k: int = 5

@app.get('/')
def root():
    return{'message':'RAG API is running'}


@app.get('/health')
def health():
    return rag.check_health()



@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = rag.add_documents(str(file_path))
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post('/query')
def query_docs(request: QureyRequest):
    try:
        result = rag.query(request.question,top_k =request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code = 500,detail=str(e))


@app.get("/documents")
def get_documents():
    return rag.get_documents_info()


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    result = rag.delete_document(doc_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result)
    return result

