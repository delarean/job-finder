from __future__ import annotations

from abc import ABC, abstractmethod


class SourceAdapter(ABC):
    @abstractmethod
    def discover(self) -> list[dict]:
        raise NotImplementedError
