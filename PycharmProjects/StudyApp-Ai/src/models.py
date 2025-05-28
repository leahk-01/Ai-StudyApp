from pydantic import BaseModel

class QARequest(BaseModel):
    query: str

class SummaryRequest(BaseModel):
    notes: str

class NotesRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str

class QuizRequest(BaseModel):
    subject: str = "general"
    num_questions: int = 5

class NotesUploadRequest(BaseModel):
    notes: str

