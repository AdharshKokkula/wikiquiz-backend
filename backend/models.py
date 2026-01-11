from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quizzes = relationship("Quiz", back_populates="owner")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Link to user
    url = Column(Text, nullable=False) # Removed unique=True, managed by unique constraint relative to user? Or just allow dupes for simplicity in "Private" mode.
    # Actually, for "Private" mode, duplicates across users are fine. Duplicates for SAME user should be handled.
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    key_entities = Column(JSON, nullable=False)  # Stores {people: [], organizations: [], locations: []}
    sections = Column(JSON, nullable=False)      # Stores definition of sections
    quiz = Column(JSON, nullable=False)          # Stores array of questions
    related_topics = Column(JSON, nullable=False) # Array of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_html = Column(Text, nullable=True)
    
    owner = relationship("User", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz_rel", cascade="all, delete-orphan")

    # If we want unique URL per user:
    # __table_args__ = (UniqueConstraint('user_id', 'url', name='_user_url_uc'),)
    # But for now, let's keep it simple. If I generate the same twice, I get two entries or I handle in logic.


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    details = Column(JSON, nullable=False) # Stores list of {question_id/index, selected, correct, etc}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz_rel = relationship("Quiz", back_populates="attempts")
