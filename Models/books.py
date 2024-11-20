from sqlalchemy import Column,Date,String,Integer
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel,validator
from datetime import date
from typing import Optional

class Base(DeclarativeBase):
    pass

class  Book(Base):
    __tablename__ = "books"
    id = Column(String, primary_key=True)
    isbn = Column(Integer, nullable=False, unique=True) #Makes ISBN unique
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    pb_date= Column(Date, nullable=False)

class UpdateBook(BaseModel):
    isbn: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    pb_date: Optional[date] = None

class BookRespond(BaseModel):
    id:int
    isbn:int
    title:str
    author:str
    pb_date:date

    class Config:
        from_attributes = True
class BookCreate(BaseModel):
    isbn:int
    title:str
    author:str
    pb_date:date

    @validator("pb_date")
    def check_date(cls,value):
        if value > date.today():
            raise ValueError("Publication date cannot be in future time")
        return value