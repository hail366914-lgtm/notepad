import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

templates = Jinja2Templates(directory="templates")

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

class NewBook(BaseModel):
    title: str
    author: str

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "notefront.html",
        {
            "request": request,
            "books": books
        }
    )

@app.get("/api/books")
def read_books():
    return books

@app.post("/api/books")
def create_book(new_book: NewBook):
    new_id = len(books) + 1
    book_entry = {
        "id": new_id,
        "title": new_book.title,
        "author": new_book.author,
    }
    books.append(book_entry)
    try:
        with open("db.json", "w", encoding="utf-8") as file:
            json.dump(books, file, indent=4, ensure_ascii=False)
    except:
        pass
    return {"success": True, "message": "Книга успешно добавлена", "book": book_entry}

try:
    with open("db.json", "r", encoding="utf-8") as file:
        loaded_books = json.load(file)
        if loaded_books:
            books = loaded_books
except:
    pass

