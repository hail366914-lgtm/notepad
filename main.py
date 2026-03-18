import json
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

def load_news():
    try:
        with open("news_db.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return [
            {
                "id": 1,
                "title": "Запуск нового космического телескопа",
                "content": "NASA успешно запустила новый космический телескоп для изучения далеких галактик.",
                "date": "2024-03-18",
                "category": "Наука"
            },
            {
                "id": 2,
                "title": "Прорыв в области искусственного интеллекта",
                "content": "Ученые представили новую нейросеть, способную решать сложные математические задачи.",
                "date": "2024-03-17",
                "category": "Технологии"
            },
            {
                "id": 3,
                "title": "Открытие нового вида морских обитателей",
                "content": "Биологи обнаружили неизвестный ранее вид глубоководных рыб в Тихом океане.",
                "date": "2024-03-16",
                "category": "Природа"
            }
        ]

def load_users():
    try:
        with open("users_db.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return [
            {
                "id": "1",
                "username": "admin",
                "password": "admin123",
                "email": "admin@example.com"
            }
        ]

def save_news(news):
    try:
        with open("news_db.json", "w", encoding="utf-8") as file:
            json.dump(news, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

def save_users(users):
    try:
        with open("users_db.json", "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

news = load_news()
users = load_users()

class NewsItem(BaseModel):
    title: str
    content: str
    category: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "news.html",
        {
            "request": request,
            "news": news
        }
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, username: Optional[str] = None, password: Optional[str] = None):
    user = None
    if username and password:
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    
    if not user:
        return RedirectResponse(url="/register", status_code=303)
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user
        }
    )

@app.get("/api/news")
def read_news():
    return news

@app.post("/api/news")
def create_news(new_item: NewsItem):
    new_id = max([item["id"] for item in news], default=0) + 1
    from datetime import datetime
    news_entry = {
        "id": new_id,
        "title": new_item.title,
        "content": new_item.content,
        "category": new_item.category,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    news.append(news_entry)
    save_news(news)
    return {"success": True, "message": "Новость успешно добавлена", "news": news_entry}

@app.post("/api/register")
def register_user(user: UserRegister):
    existing_user = next((u for u in users if u["username"] == user.username), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    existing_email = next((u for u in users if u["email"] == user.email), None)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    new_user = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "password": user.password,
        "email": user.email
    }
    users.append(new_user)
    save_users(users)
    return {"success": True, "message": "Регистрация успешна", "user": new_user}

@app.post("/api/login")
def login_user(user: UserLogin):
    existing_user = next((u for u in users if u["username"] == user.username and u["password"] == user.password), None)
    if not existing_user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    return {"success": True, "message": "Вход выполнен успешно", "user": existing_user}

@app.delete("/api/news/{news_id}")
def delete_news(news_id: int):
    global news
    news_item = next((n for n in news if n["id"] == news_id), None)
    if not news_item:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    news = [n for n in news if n["id"] != news_id]
    save_news(news)
    return {"success": True, "message": "Новость успешно удалена"}
