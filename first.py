from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from Models.books import Book,BookRespond,BookCreate,UpdateBook
from Models.database import SessionLocal

app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/books",response_model = BookRespond)
def get_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = Book(
        isbn = book.isbn,
        title = book.title,
        author = book.author,
        pb_date = book.pb_date)
    db.add(new_book)
    try:
        db.commit()
        db.refresh(new_book)
    except IntegrityError: #try to insert a new book with an existing ISBN
        db.rollback()
        raise HTTPException(status_code=400,detail = "ISBN must be unique")
    return new_book


@app.get("/books", response_model = list[BookRespond])
def return_books(db: Session = Depends(get_db)):
    books = db.execute(select(Book)).scalars().all()
    return books



@app.get("/books/{book_id}", response_model=BookRespond)
async def get_particular_details(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id) #Query Database for that book
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book



@app.delete("/books/{book_id}", response_model=BookRespond)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    # Query the database for the book with the specified ID
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()

    return book

@app.put("/books/{book_id}", response_model=BookRespond)
async def update_book(book_id: int, book_data: UpdateBook, db: Session = Depends(get_db)):
    # Retrieve the book by ID
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    # Update only the fields provided in the request
    update_data = book_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)  # Dynamically set the attribute

    # Attempt to commit changes to the database
    try:
        db.commit()
        db.refresh(book)  # Refresh to get the updated data
    except IntegrityError:
        db.rollback()  # Rollback in case of integrity error
        raise HTTPException(status_code=400, detail="ISBN must be unique")