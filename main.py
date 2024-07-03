from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import create_engine, Session, select
from models import *
from config import sqlite_url

app = FastAPI()

engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/quizzes/{quizz_id}", response_model=QuizzPublicWithQuestions)
async def read_quizz(*, session: Session = Depends(get_session), quizz_id):
    return session.get(Quizz, quizz_id)

@app.get("/quizzes", response_model=list[QuizzPublicWithQuestions])
async def read_quizz(*, session: Session = Depends(get_session)):
    return session.exec(select(Quizz)).all()
