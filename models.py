from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    id: str
    status: str = "pending"
    progress: int = 0
    file_content: Optional[bytes] = None
    language: str = "ru"
    result_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)