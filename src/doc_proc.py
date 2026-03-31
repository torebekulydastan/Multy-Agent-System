from pathlib import Path
from typing import List
import re

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )


    def clean_text(self, text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # 🔹 2. Choose loader
    def load_single_file(self, file_path: Path) -> List[Document]:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        elif suffix == ".csv":
            loader = CSVLoader(str(file_path))
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        return loader.load()

    # 🔹 3. Load all files
    def load_documents(self, data_dir: str) -> List[Document]:
        data_path = Path(data_dir).resolve()
        print(f"[DEBUG] Data path: {data_path}")

        if not data_path.exists():
            raise FileNotFoundError(f"Directory not found: {data_path}")

        documents: List[Document] = []

        patterns = ["**/*.pdf", "**/*.txt", "**/*.csv", "**/*.docx"]
        all_files = []

        for pattern in patterns:
            all_files.extend(data_path.glob(pattern))

        print(f"[DEBUG] Found {len(all_files)} files")

        for file_path in all_files:
            print(f"[DEBUG] Loading: {file_path}")
            try:
                loaded = self.load_single_file(file_path)

                for doc in loaded:
                    doc.page_content = self.clean_text(doc.page_content)
                    doc.metadata["source"] = str(file_path)
                    doc.metadata["file_name"] = file_path.name
                    doc.metadata["file_type"] = file_path.suffix.lower()

                documents.extend(loaded)

            except Exception as e:
                print(f"[ERROR] Failed to load {file_path}: {e}")

        print(f"[DEBUG] Total raw documents: {len(documents)}")
        return documents

    # 🔹 4. Split into chunks
    def split_documents(self, documents: List[Document]) -> List[Document]:
        chunks = self.splitter.split_documents(documents)

        for i, doc in enumerate(chunks):
            doc.metadata["chunk_id"] = i
            doc.metadata["chunk_length"] = len(doc.page_content)

        print(f"[DEBUG] Total chunks: {len(chunks)}")
        return chunks

    # 🔹 5. Full pipeline
    def process(self, data_dir: str) -> List[Document]:
        raw_docs = self.load_documents(data_dir)
        chunks = self.split_documents(raw_docs)
        return chunks

    def process_uploaded_file(self, file_path: str):
        """
        Совместимость с `RAGEngine.add_documents()`.

        Returns:
            (documents, metadata)
            documents: List[{"text": str, "metadata": dict}]
            metadata: dict (общая инфо по файлу)
        """
        path = Path(file_path).resolve()
        loaded = self.load_single_file(path)

        for doc in loaded:
            doc.page_content = self.clean_text(doc.page_content)
            doc.metadata["source"] = str(path)
            doc.metadata["file_name"] = path.name
            doc.metadata["file_type"] = path.suffix.lower()

        chunks = self.split_documents(loaded)

        documents = [{"text": c.page_content, "metadata": dict(c.metadata)} for c in chunks]
        metadata = {
            "source": str(path),
            "file_name": path.name,
            "file_type": path.suffix.lower(),
            "chunks": len(documents),
        }
        return documents, metadata