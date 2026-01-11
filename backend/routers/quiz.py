from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Quiz, QuizAttempt, User
from schemas import QuizGenerateRequest, QuizOut, QuizListElement, QuizAttemptCreate, QuizAttemptOut
from services.scraper import WikipediaScraper
from services.llm import LLMService
from routers.auth import get_current_user
import traceback

router = APIRouter()
scraper = WikipediaScraper()
# We instantiate LLM service here or per request. 
try:
    llm_service = LLMService()
except Exception:
    llm_service = None

@router.post("/generate-quiz", response_model=QuizOut)
def generate_quiz(
    request: QuizGenerateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check Cache (User Specific)
    # We check if *this user* already has a quiz for this URL.
    existing_quiz = db.query(Quiz).filter(
        Quiz.url == str(request.url),
        Quiz.user_id == current_user.id
    ).first()

    if existing_quiz:
        if request.difficulty == "random":
             return existing_quiz
        else:
             # Refresh for specific difficulty
             db.delete(existing_quiz)
             db.commit()

    # 2. Scrape
    try:
        scraped_data = scraper.scrape(str(request.url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    # 3. LLM Generation
    if not llm_service:
        raise HTTPException(status_code=500, detail="LLM Service not initialized")
    
    try:
        # Pass difficulty param
        llm_data = llm_service.generate_quiz_data(
            scraped_data["full_text"], 
            difficulty=request.difficulty
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"LLM generation failed: {str(e)}")

    # 4. Save to DB (Associated with User)
    new_quiz = Quiz(
        user_id=current_user.id,
        url=str(request.url),
        title=scraped_data["title"],
        summary=scraped_data["summary"],
        sections=scraped_data["sections"],
        key_entities=llm_data["key_entities"],
        quiz=llm_data["quiz"],
        related_topics=llm_data["related_topics"],
        raw_html=scraped_data.get("raw_html")
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return new_quiz



@router.get("/quizzes", response_model=list[QuizListElement])
def get_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Filter by user
    quizzes = db.query(Quiz).filter(Quiz.user_id == current_user.id).all()
    
    results = []
    for q in quizzes:
        top = 0
        if q.attempts:
            top = max([a.score for a in q.attempts])
        
        results.append(QuizListElement(
            id=q.id,
            url=q.url,
            title=q.title,
            created_at=q.created_at,
            top_score=top if q.attempts else None
        ))
    return results

@router.get("/quizzes/{quiz_id}", response_model=QuizOut)
def get_quiz_details(quiz_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Filter by ID and User
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    top = 0
    if quiz.attempts:
        top = max([a.score for a in quiz.attempts])
        
    return QuizOut(
        id=quiz.id,
        url=quiz.url,
        title=quiz.title,
        summary=quiz.summary,
        key_entities=quiz.key_entities,
        sections=quiz.sections,
        quiz=quiz.quiz,
        related_topics=quiz.related_topics,
        created_at=quiz.created_at,
        top_score=top if quiz.attempts else None
    )

@router.post("/attempts", response_model=QuizAttemptOut)
def submit_attempt(
    attempt: QuizAttemptCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify quiz exists AND belongs to user
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    details_json = [d.model_dump() for d in attempt.details]

    db_attempt = QuizAttempt(
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        max_score=attempt.max_score,
        details=details_json
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt
