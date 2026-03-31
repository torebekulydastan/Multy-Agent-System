from fastembed import TextEmbedding
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class FastEmbedEmbeddings:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = TextEmbedding(model_name=self.model_name)

    def _get_embedding(self, text: str) -> List[float]:
        try:
            clean_text = text if text.strip() else " "

            embedding = next(self.model.query_embed(clean_text))
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            clean_texts = [text if text.strip() else " " for text in texts]

            embeddings = list(self.model.passage_embed(clean_texts))
            result = [emb.tolist() for emb in embeddings]

            logger.info(f"Processed {len(texts)} documents for embeddings")
            return result

        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)

    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        if isinstance(texts, str):
            return self.embed_query(texts)
        return self.embed_documents(texts)

    def validate_model(self) -> bool:
        try:
            test_embedding = self._get_embedding("test")
            logger.info(f"Model {self.model_name} is available. Dim={len(test_embedding)}")
            return True
        except Exception as e:
            logger.error(f"Model {self.model_name} is unavailable: {e}")
            return False

    
            