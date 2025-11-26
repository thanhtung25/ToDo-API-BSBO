# main.py
from fastapi import FastAPI
from routers import tasks,stats

app = FastAPI(
    title="ToDo API",
    description="API для управления задачачи с использованием матрицы Эйзенхауэра",
    version="1.0",
    contact={"name": "Нгуен Кхак Тхань Тунг"},
)

app.include_router(tasks.router, prefix="/api/v1")

@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact("name"),
            }