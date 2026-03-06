import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

def load_books():
    try:
        with open("db.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return [
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

def save_books(books):
    try:
        with open("db.json", "w", encoding="utf-8") as file:
            json.dump(books, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

books = load_books()

class NewBook(BaseModel):
    title: str
    author: str

class DeleteBooksRequest(BaseModel):
    book_ids: List[int]

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "notefront.html",
        {
            "request": request,
            "books": books
        }
    )

@app.get("/del", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse(
        "del.html",
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
    new_id = max([book["id"] for book in books], default=0) + 1
    book_entry = {
        "id": new_id,
        "title": new_book.title,
        "author": new_book.author,
    }
    books.append(book_entry)
    save_books(books)
    return {"success": True, "message": "Книга успешно добавлена", "book": book_entry}

@app.delete("/api/books/{book_id}")
def delete_book(book_id: int):
    global books
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    books = [b for b in books if b["id"] != book_id]
    save_books(books)
    return {"success": True, "message": "Книга успешно удалена"}

@app.delete("/api/books")
def delete_multiple_books(request: DeleteBooksRequest):
    global books
    if not request.book_ids:
        raise HTTPException(status_code=400, detail="Не указаны книги для удаления")
    
    books = [b for b in books if b["id"] not in request.book_ids]
    save_books(books)
    return {"success": True, "message": f"Успешно удалено {len(request.book_ids)} книг"}

