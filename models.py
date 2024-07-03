from sqlmodel import Field, SQLModel, Relationship

class QuizzBase(SQLModel):
    name: str
    difficulty: int = 1
    category: str | None = Field(default=None)

class Quizz(QuizzBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    questions: list["Question"] = Relationship(back_populates="quizz")

class QuestionBase(SQLModel):
    content: str = Field(nullable=False)
    quizz_id: int | None = Field(default=None, foreign_key="quizz.id")

class Question(QuestionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quizz: Quizz = Relationship(back_populates="questions")
    answers: list["Answer"] = Relationship(back_populates="question")

class AnswerBase(SQLModel):
    content: str = Field(nullable=False)
    valid: bool = Field(default=False)
    question_id: int | None = Field(default=None, foreign_key="question.id")

class Answer(AnswerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question: Question | None = Relationship(back_populates="answers")

class AnswerPublic(AnswerBase):
    id: int

class QuestionPublic(QuestionBase):
    id: int

class QuestionPublicWithAnswers(QuestionPublic):
    answers: list[AnswerPublic] = []

class QuizzPublic(QuizzBase):
    id: int

class QuizzPublicWithQuestions(QuizzPublic):
    questions: list[QuestionPublicWithAnswers] = []
