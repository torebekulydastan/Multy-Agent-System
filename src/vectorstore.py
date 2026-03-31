from typing import List, Dict, Optional
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from .embeddings import FastEmbedEmbeddings

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    def __init__(
        self,
        embeddings_model: FastEmbedEmbeddings,
        collection_name: str = "documents",
        host: str = "localhost",
        port: int = 6333
    ):
        self.embeddings = embeddings_model
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        self._collection_ready = False

    def ensure_collection(self) -> None:
        if self._collection_ready:
            return
        self.create_collection()
        self._collection_ready = True

    def create_collection(self) -> None:
        test_vector = self.embeddings.embed_query("test")
        vector_size = len(test_vector)

        collections = self.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' created")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")

    def add_documents(
        self,
        documents: List[Dict],
        metadatas: Optional[List[Dict]] = None
    ) -> List[str]:
        self.ensure_collection()
        if not documents:
            return []

        if metadatas is None:
            metadatas = [{} for _ in documents]

        texts = [doc["text"] for doc in documents]
        vectors = self.embeddings.embed_documents(texts)

        points = []
        ids = []

        for text, vector, metadata in zip(texts, vectors, metadatas):
            point_id = str(uuid.uuid4())
            ids.append(point_id)

            payload = {
                "text": text,
                **metadata
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Added {len(points)} documents to Qdrant")
        return ids

    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        self.ensure_collection()
        query_vector = self.embeddings.embed_query(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=k,
            with_payload=True
        ).points

        output = []
        for point in results:
            output.append({
                "id": point.id,
                "score": point.score,
                "text": point.payload.get("text", ""),
                "metadata": point.payload
            })

        return output

    def delete_document(self, doc_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[doc_id],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def get_document_count(self) -> int:
        try:
            collections = self.client.get_collections().collections
            existing_names = [c.name for c in collections]

            if self.collection_name not in existing_names:
                return 0

            info = self.client.get_collection(self.collection_name)
            return int(getattr(info, "points_count", 0) or 0)
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return 0

    def get_all_documents(self, limit: int = 100) -> List[Dict]:
        try:
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            out: List[Dict] = []
            for p in points:
                payload = p.payload or {}
                out.append(
                    {
                        "id": str(p.id),
                        "text": payload.get("text", ""),
                        "metadata": payload,
                    }
                )
            return out
        except Exception as e:
            logger.error(f"Failed to scroll documents: {e}")
            return []