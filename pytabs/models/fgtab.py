from dataclasses import dataclass
from typing import Callable


@dataclass
class Tab:
    id: str
    title: str
    content: Callable
