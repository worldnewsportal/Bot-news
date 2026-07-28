from abc import ABC, abstractmethod
from typing import List
from models.article import Article

class BaseCollector(ABC):
    @abstractmethod
    async def collect(self) -> List[Article]:
        pass
