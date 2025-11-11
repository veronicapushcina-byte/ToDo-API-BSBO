# Главный файл приложения
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Постоленко Виктория Сергеевна"
    }
)
app.include_router(tasks.router)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]


@app.get("/")
async def welcome() -> dict:
    return { "message": "Привет, студент!",
             "api_title": app.title,
             "api_description": app.description,
             "api_version": app.version,
             "api_authors": app.contact["name"]}

@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db), # считает количество записей в хранилище
        "tasks": tasks_db # выводит всё, чта есть в хранилище
    }

@app.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException( #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4" #текст, который будет
        )
    filtered_tasks = [
        task # ЧТО добавляем в список
        for task in tasks_db # ОТКУДА берем элементы
        if task["quadrant"] == quadrant # УСЛОВИЕ фильтрации
    ]
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
}

@app.get("/tasks/task/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    if task_id > 4 or task_id < 0:
        raise HTTPException( #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке
            status_code=404,
            detail="Invalid task_id" #текст, который будет
        )
    task = {}
    for val in tasks_db:
        if val["id"] == task_id:
            task = val
    return {
        "task": task
    }

@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    lenTasks = len(tasks_db)
    lenCompletedTasks = 0
    lenUnCompletedTasks = 0
    lenQOne = 0
    lenQTwo = 0
    lenQThree = 0
    lenQFour = 0
    for val in tasks_db:
        if val["completed"]:
            lenCompletedTasks+=1
        else:
            lenUnCompletedTasks+=1
        if val["quadrant"] == "Q1":
            lenQOne+=1
        elif val["quadrant"] == "Q2":
            lenQTwo+=1
        elif val["quadrant"] == "Q3":
            lenQThree+=1
        elif val["quadrant"] == "Q4":
            lenQFour+=1
    return {
        "total_tasks": lenTasks,
        "by_quadrant": {
            "Q1": lenQOne,
            "Q2": lenQTwo,
            "Q3": lenQThree,
            "Q4": lenQFour
        },
        "by_status": {
            "completed": lenCompletedTasks,
            "pending": lenUnCompletedTasks
        }
    }

@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid q"
        )
    resultTasks = []
    for val in tasks_db:
        if q in (val.get("title") or "") or q in (val.get("description") or ""):
            resultTasks.append(val)
    if len(resultTasks) == 0:
        raise HTTPException(
            status_code=404,
            detail="not found with this q"
        )
    return {
        "query": q,
        "count": len(resultTasks),
        "tasks": resultTasks
    }

@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="invalid status"
        )
    completed = False
    if status == "completed":
        completed = True
    resultTasks = []
    for val in tasks_db:
        if val["completed"] == completed:
            resultTasks.append(val)
    return {
        "status": status,
        "count": len(resultTasks),
        "tasks": resultTasks
    }
