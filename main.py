from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import create_engine, Session, select
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

from models import *
from config import sqlite_url

app = FastAPI()
load_dotenv()

engine = create_engine(sqlite_url, echo=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


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

def fake_decode_token(token):
    return token

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == fake_decode_token(token))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

def fake_hash_password(password: str):
    return "fakehashed" + password

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
