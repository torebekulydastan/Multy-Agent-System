from langchain.tools import tool 
from src.vectorstore import QdrantVectorStore
from .doc_proc import DocumentProcessor
from .embeddings import FastEmbedEmbeddings
import logging 
from config import Config
import os 
import sys
from config import RAG_PROMPT_TEMPLATE
from pathlib import Path

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.embeddings = FastEmbedEmbeddings()
        self.vectorstore= QdrantVectorStore(embeddings_model=self.embeddings)
        self.document_processor = DocumentProcessor()

        # Явно грузим .env из корня проекта, чтобы ключи были доступны
        # и в процессе перезагрузчика uvicorn на Windows.
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path, override=True)

        api_key = os.getenv("API_KEY")
        if api_key:
            self.llm = ChatDeepSeek(
                model="deepseek-chat",
                api_key=api_key,
                temperature=0.2,
                max_tokens=1024,
            )
        else:
            self.llm = None


    def add_documents(self,file_path):
        try:
            documents,metadata = self.document_processor.process_uploaded_file(file_path)

            if not documents:
                raise ValueError('couldnt extract documents from the file')


            doc_ids = self.vectorstore.add_documents(
                documents = [{'text':doc['text'] } for doc in documents],
                metadatas= [doc['metadata'] for doc in documents]
            )


            result = {
                'success':True,
                'file_path':file_path,
                'documents_added':len(doc_ids),
                'chunk_count':len(documents),
                'metadata':metadata,
                'documents_ids':doc_ids[:10]
            }

            logger.info(f"added {len(doc_ids)} documents from the file {file_path}")
            return result



        except Exception as e:
            logger.error(f"error while adding the document {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    def retrive_relevan_documents(self,query,k=5):

        try:
            relevant_docs = self.vectorstore.similarity_search(query,k)

            if not relevant_docs:
                logger.warning('dont found relative document')
                return []

            logger.info(f"found {len(relevant_docs)} relevant docs")
            return relevant_docs

        except Exception as e:
            logger.error(f'error when searchin the documents:{e}')
            return []

    def generate_response(self,query,context_docs=None,**kwargs):
        try:
            if self.llm is None:
                return "error deep seek api key is not loaded"
            # Получаем контекст если не передан
            if context_docs is None:
                context_docs = self.retrieve_relevant_documents(query)
            
            # Формируем контекст
            if context_docs:
                context_text = "\n\n".join([
                    f"document {i+1}:\n{doc['text']}"
                    for i, doc in enumerate(context_docs)
                ])
            else:
                context_text = "context is no found"
            
            # Формируем промпт
            prompt = RAG_PROMPT_TEMPLATE.format(
                context=context_text,
                question=query
            )


            

            response =  self.llm.invoke(prompt)

            answer = response.content.strip()


            logger.info(f"generated answer with len {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"error while generating the answer {e}")
            return f"error while generating the answer {str(e)}"
    


    def query(self,question,**kwargs):


        try:
            relevant_docs = self.retrive_relevan_documents(question,k = kwargs.get('top_k',Config.RAG.TOP_K_RESULTS))


            answer  =self.generate_response(question,context_docs=relevant_docs,**kwargs)

            result = {
                "question": question,
                "answer": answer,
                "relevant_documents": [
                    {
                        "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                        "score": doc["score"],
                        "metadata": doc["metadata"]
                    }
                    for doc in relevant_docs
                ],
                "documents_count": len(relevant_docs),
                "success": True
            }
            
            return result



        except Exception as e:
            logger.error(f"error while the processing document: {e}")
            return {
                "question": question,
                "answer": f"error{str(e)}",
                "relevant_documents": [],
                "documents_count": 0,
                "success": False,
                "error": str(e)
            }


    def delete_document(self, doc_id):
        """delete the document from the system"""
        try:
            success = self.vectorstore.delete_document(doc_id)
            return {
                "success": success,
                "document_id": doc_id,
                "message": "document is deleted" if success else "document is not found"
            }
        except Exception as e:
            logger.error(f"error while deleting the document: {e}")
            return {
                "success": False,
                "document_id": doc_id,
                "error": str(e)
            }

    def get_documents_info(self):
        try:
            documents = self.vectorstore.get_all_documents()

            return {
                'total_documents':len(documents),
                'documents':documents,
                'success':True
            }

        except Exception as e:
            logger.error(f"errro when the gettign the info from the document: {e}")
            return {
                "total_documents": 0,
                "documents": [],
                "success": False,
                "error": str(e)
            }
    def check_health(self) -> dict:
    
        try:
            env_path = Path(__file__).resolve().parents[1] / ".env"
            load_dotenv(dotenv_path=env_path, override=True)
            # Проверяем embeddings
            embeddings_ok = self.embeddings.validate_model()

        # Проверяем наличие API ключа
            api_key_ok = bool(os.getenv("DEEPSEEK_API_KEY"))

        # Проверяем DeepSeek
            llm_ok = False
            llm_error = None

            if api_key_ok:
                try:
                    test_response = self.llm.invoke("Say only: OK")
                    if test_response and hasattr(test_response, "content"):
                        llm_ok = True
                except Exception as e:
                    llm_error = str(e)

        # Проверяем векторное хранилище
            try:
                vector_store_docs = self.vectorstore.get_document_count()
                vector_store_ok = True
            except Exception as e:
                vector_store_docs = 0
                vector_store_ok = False

            return {
            "embeddings_ok": embeddings_ok,
            "api_key_ok": api_key_ok,
            "llm_model": "deepseek-chat",
            "llm_ok": llm_ok,
            "llm_error": llm_error,
            "vector_store_ok": vector_store_ok,
            "vector_store_docs": vector_store_docs,
            "system_ok": embeddings_ok and api_key_ok and llm_ok and vector_store_ok
        }

        except Exception as e:
            logger.error(f"error while cheking the system{e}")
            return {
            "system_ok": False,
            "error": str(e)
        }


