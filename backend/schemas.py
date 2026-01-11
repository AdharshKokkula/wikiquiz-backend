from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

# --- Input Schemas ---
class QuizGenerateRequest(BaseModel):
    url: HttpUrl
    difficulty: str = "random" # easy, medium, hard, random

# --- Output Schemas ---

class KeyEntities(BaseModel):
    people: List[str]
    organizations: List[str]
    locations: List[str]

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    difficulty: str
    explanation: str

class QuizOut(BaseModel):
    id: int
    url: str
    title: str
    summary: str
    key_entities: KeyEntities
    sections: List[str]
    quiz: List[QuizQuestion]
    related_topics: List[str]
    created_at: datetime
    top_score: Optional[int] = None

class QuizListElement(BaseModel):
    id: int
    url: str
    title: str
    created_at: datetime
    top_score: Optional[int] = None

class AttemptDetail(BaseModel):
    question_index: int
    selected_option: str
    is_correct: bool

class QuizAttemptCreate(BaseModel):
    quiz_id: int
    score: int
    max_score: int
    details: List[AttemptDetail]

class AttemptDetail(BaseModel):
    question_index: int
    selected_option: str
    is_correct: bool

class QuizAttemptCreate(BaseModel):
    quiz_id: int
    score: int
    max_score: int
    details: List[AttemptDetail]

class QuizAttemptOut(BaseModel):
    id: int
    quiz_id: int
    score: int
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ErrorResponse(BaseModel):
    detail: str
