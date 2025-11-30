# Главный файл приложения
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from routers import tasks

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Постоленко Виктория Сергеевна"
    }
)

app.include_router(tasks.router, prefix="/api/v1") # подключение pоутера к приложению

@app.get("/")   
async def welcome() -> dict:
    return { "message": "Привет, студент!",
             "api_title": app.title,
             "api_description": app.description,
             "api_version": app.version,
             "api_authors": app.contact["name"]}

@app.post("/tasks")
async def create_task(task: dict):
    return {"message": "Запись успешно создана!", "task": task}

    