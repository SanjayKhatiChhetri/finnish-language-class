from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

class StreamItemType(Enum):
    ANNOUNCEMENT = "ANNOUNCEMENT"
    ASSIGNMENT = "ASSIGNMENT"

class AttachmentType(Enum):
    PDF = "PDF"
    VIDEO = "VIDEO"
    DOCS = "DOCS"
    IMAGE = "IMAGE"
    LINK = "LINK"

@dataclass
class Attachment:
    type: AttachmentType
    title: str
    url: str

@dataclass
class StreamItem:
    id: str
    type: StreamItemType
    author: str
    date: str
    deleted: bool
    content: str
    attachments: List[Attachment]

@dataclass
class WeeklyData:
    display_name: str
    items: List[StreamItem]
