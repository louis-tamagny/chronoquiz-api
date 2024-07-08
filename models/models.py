from sqlmodel import Field, SQLModel, Relationship


# Base models with class attributes for data validation

class QuizzBase(SQLModel):
    name: str
    difficulty: int = 1
    category: str | None = Field(default=None)

class QuestionBase(SQLModel):
    content: str = Field(nullable=False)
    quizz_id: int | None = Field(default=None, foreign_key="quizz.id")

class AnswerBase(SQLModel):
    content: str = Field(nullable=False)
    valid: bool = Field(default=False)
    question_id: int | None = Field(default=None, foreign_key="question.id")

class UserBase(SQLModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class QuizzSessionBase(SQLModel):
    user_id: int | None = Field(default=None, foreign_key="user.id")
    quizz_id: int | None = Field(default=None, foreign_key="quizz.id")
    score: int = Field(default=0)

class QuizzSessionAnswersBase(SQLModel):
    quizz_session_id: int | None = Field(default=None, foreign_key="quizzsession.id")
    answer_id: int | None = Field(default=None, foreign_key="answer.id")

# Models used for database manipulation

class Quizz(QuizzBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    questions: list["Question"] = Relationship(back_populates="quizz")

class Question(QuestionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quizz: Quizz = Relationship(back_populates="questions")
    answers: list["Answer"] = Relationship(back_populates="question")

class Answer(AnswerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question: Question | None = Relationship(back_populates="answers")

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    quizz_sessions: list["QuizzSession"] = Relationship(back_populates="user")

class QuizzSession(QuizzSessionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: User | None = Relationship(back_populates="quizz_sessions")
    quizz: Quizz | None = Relationship()
    answers: list["QuizzSessionAnswers"] = Relationship(back_populates="quizz_session")

class QuizzSessionAnswers(QuizzSessionAnswersBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quizz_session: QuizzSession | None = Relationship(back_populates="answers")
    answer: Answer | None = Relationship()


# Models used in public facing interfaces

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

class QuizzSessionPublic(QuizzSessionBase):
    id: int
    quizz: QuizzPublic
    answers: list[AnswerPublic] = []

class UserPublic(UserBase):
    id: int
    quizz_sessions: list[QuizzSessionPublic] = []

# Models used for authentication

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None
