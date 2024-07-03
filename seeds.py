from sqlmodel import Session, create_engine
from models import Quizz, Question, Answer
from config import sqlite_url

engine = create_engine(sqlite_url)

quizz_1 = Quizz(name="Guerre de trente ans", difficulty=3)
quizz_2 = Quizz(name="Révolution industrielle", difficulty=2)
quizz_3 = Quizz(name="Population et territoires", difficulty=4)

with Session(engine) as session:
    session.add(quizz_1)
    session.add(quizz_2)
    session.add(quizz_3)
    session.commit()

question_1 = Question(content="Début de la guerre ?", quizz=quizz_1)

with Session(engine) as session:
    session.add(question_1)
    session.commit()

answer_1 = Answer(content="1338", valid=True, question=question_1)
answer_2 = Answer(content="2004", valid=False, question=question_1)
answer_3 = Answer(content="1348", valid=False, question=question_1)
answer_4 = Answer(content="1326", valid=False, question=question_1)

with Session(engine) as session:
    session.add_all((answer_1, answer_2, answer_3, answer_4))
    session.commit()
