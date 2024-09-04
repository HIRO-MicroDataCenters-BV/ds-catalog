from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    full_name: str
