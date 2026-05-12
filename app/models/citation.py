from pydantic import BaseModel


class Citation(BaseModel):
    id: int
    doc_id: str
    doc_title: str
    section: str
    text: str
    score: float

