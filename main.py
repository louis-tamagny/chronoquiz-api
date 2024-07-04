from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated

from sqlmodel import create_engine, Session, select
from models import *
from config import sqlite_url

app = FastAPI()

engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/quizzes/{quizz_id}", response_model=QuizzPublicWithQuestions)
async def read_quizz(*, session: Session = Depends(get_session), token: Annotated[str, Depends(oauth2_scheme)], quizz_id):
    return session.get(Quizz, quizz_id)

@app.get("/quizzes", response_model=list[QuizzPublicWithQuestions])
async def read_quizz(*, session: Session = Depends(get_session)):
    return session.exec(select(Quizz)).all()

@app.post("/quizzes", response_model=QuizzPublicWithQuestions)
async def create_quizz(quizz: Quizz, session: Session = Depends(get_session)):
    session.add(quizz)
    session.commit()
    session.refresh(quizz)
    return quizz

@app.post("/quizzes/{quizz_id}/questions", response_model=QuizzPublicWithQuestions)
async def create_question(question: Question, quizz_id: int, session: Session= Depends(get_session)):
    quizz = session.get(Quizz, quizz_id)
    question.quizz = quizz
    session.add(question)
    session.commit()
    session.refresh(quizz)
    return quizz

@app.post("/questions/{question_id}/answers", response_model=QuestionPublicWithAnswers)
async def create_answers(answers: list[Answer], question_id: int, session: Session= Depends(get_session)):
    q = session.get(Question, question_id)
    for a in answers:
        a.question = q
        session.add(a)
    session.commit()
    session.refresh(q)
    return q
