from fastapi import FastAPI,UploadFile,File,HTTPException
from pydantic import BaseModel
import shutil
from pathlib import Path
from RAG_AGENT.agent import run_agentic_rag
from src.rag_engine import RAGEngine
from config import Config
from src.chat_history import MongoChatHistory
app = FastAPI(title='rag api')

rag = RAGEngine()

chat_history_store = MongoChatHistory(
    mongo_uri=Config.MONGO_URI,
    db_name=Config.MONGO_DB_NAME
)


UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok = True)


class RAG_AgentRequest(BaseModel):
    question:str
    session_id:str|None=None
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

@app.post('/rag_agent')
def agent_query(request: RAG_AgentRequest):
    try:
        result = run_agentic_rag(question=request.question,session_id=request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.post('/query')
def query_docs(request: QureyRequest):
    try:
        result = rag.query(request.question,top_k =request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code = 500,detail=str(e))


@app.get("/messages/grouped")
def get_messages_grouped():
    try:
        sessions = chat_history_store.list_sessions(limit=50)

        if not sessions:
            return {
                "message": "No sessions found",
                "sessions": []
            }

        result = []

        for session in sessions:
            session_id = session["_id"]
            messages = chat_history_store.get_messages(session_id=session_id, limit=10)

            result.append({
                "session_id": session_id,
                "messages": messages
            })

        return {
            "count": len(result),
            "sessions": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def get_documents():
    return rag.get_documents_info()


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    result = rag.delete_document(doc_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result)
    return result

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    try:
        deleted = chat_history_store.delete_session(session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "deleted": True,
            "message": "Session and all messages deleted"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))