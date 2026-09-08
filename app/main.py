import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.book import router as book_router
from app.borrowing import router as borrowing_router
from app.database import init_db
from app.users import router as user_router
app=FastAPI()
init_db()
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads")
os.makedirs('avatars',exist_ok=True)
app.mount("/avatars",StaticFiles(directory="avatars"),name="avatars")
app.include_router(user_router)
app.include_router(book_router)
app.include_router(borrowing_router)
