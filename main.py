from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import create_engine, Session, select
from sqlalchemy.orm import selectinload, subqueryload
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv

from models.models import *
from config import sqlite_url

app = FastAPI()
load_dotenv()

engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    with Session(engine) as session:
        user = session.exec(select(User)
                            .where(User.username == username)
                            .options(selectinload(User.quizz_sessions).selectinload(QuizzSession.quizz), selectinload(User.quizz_sessions).selectinload(QuizzSession.answers).selectinload(QuizzSessionAnswers.answer))).first()
        return user

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"])
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(token)
        payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[os.environ["ALGORITHM"]])
        print(payload)
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Paths

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

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me", response_model=UserPublic)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    print(current_user, current_user.quizz_sessions)
    return current_user
