import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

books = [
    {
        "id": 1,
        "title": "Асинхронность в Python",
        "author": "Мэттью",
    },
    {
        "id": 2,
        "title": "Backend разработка в Python",
        "author": "Артем",
    },
]

@app.get(
    "/books",
    tags=["Книги"],
    summary="Получить все книги"
)
def read_books():
    return books

@app.get("/books/{id}",
         tags=["Книги"],
         summary="Получить конкретную книгу"
         )
def get_book(id: int):
    for book in books:
        if book["id"] == id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

class NewBook(BaseModel):
    title: str
    author: str

@app.post("/books",
          tags = ["Книги"],
          summary="Добавить книгу"
          )
def create_book(new_book: NewBook):
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    bookdict = dict(new_book)
    with open("db.json", "w") as file:
        file.write(json.dumps(bookdict, indent=4))
    return bookdict, {"succes": True, "message": "Книга успешно добавлена"}



