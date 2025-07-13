from abc import ABC, abstractmethod
from pathlib import Path

from langchain_community.vectorstores import FAISS

# from langchain_openai.embeddings import OpenAIEmbeddings
# from money_manager.config import config
from money_manager.settings import FAISS_DIR
from tbot.ai.utils import SuppressTokenErrorsMixin


class MemoryRAGBase(ABC):
    def __init__(self, user_id: int, persist_dir: Path = FAISS_DIR):
        self.user_id = user_id
        self.persist_dir = persist_dir
        self.index_path = persist_dir / f"{user_id}.faiss"
        self.doc_path = persist_dir / f"{user_id}.pkl"
        self.embedding = None  # OpenAIEmbeddings(api_key=config.openai.api_key)
        self.vectorstore = self._get_vectorstore()

    def _get_vectorstore(self) -> FAISS:
        if self.index_path.exists():
            return FAISS.load_local(
                str(self.persist_dir),
                self.embedding,
                index_name=str(self.user_id),
                allow_dangerous_deserialization=True,
            )
        return FAISS.from_texts([""], self.embedding)

    @abstractmethod
    def add(
        self, texts: list[str], metadatas: list[dict], ids: list[str] | None = None
    ):
        pass

    @abstractmethod
    def search(self, query: str, k: int = 3) -> list[str]:
        pass

    @abstractmethod
    def delete(self, doc_id: str) -> None:
        pass

    @abstractmethod
    def reset(self):
        pass


class UserMemoryRAG(MemoryRAGBase, SuppressTokenErrorsMixin):
    def add(
        self, texts: list[str], metadatas: list[dict], ids: list[str] | None = None
    ):
        self.vectorstore.add_texts(texts, metadatas=metadatas, ids=ids)
        self.vectorstore.save_local(str(self.persist_dir), index_name=str(self.user_id))

    def search(self, query: str, k: int = 3) -> list[str]:
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def delete(self, doc_id: str) -> None:
        self.vectorstore.delete(ids=[doc_id])
        self.vectorstore.save_local(str(self.persist_dir), index_name=str(self.user_id))

    def reset(self):
        for path in [self.index_path, self.doc_path]:
            if path.exists():
                path.unlink()
