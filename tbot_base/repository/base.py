from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def select(self, first: bool, **kwargs):
        pass

    @abstractmethod
    def upsert(self, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs):
        pass
