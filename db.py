from sqlmodel import SQLModel, create_engine
from models import *
from config import sqlite_url

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
