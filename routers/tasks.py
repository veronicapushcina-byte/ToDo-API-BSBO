from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
from schemas import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from database import tasks_db


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={400: {"description": "Task not found"}},
)

@rouer.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db), # считает количество записей в хранилище
        "tasks": tasks_db # выводит всё, чта есть в хранилище
    }

@rouer.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException( 
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
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

@router.get("/{task_id}", response_model=TaskResponse) 
async def get_task_by_id(task_id: int) -> TaskResponse: 
    if task_id > 4 or task_id < 0:
        raise HTTPException( 
            status_code=404,
            detail="Invalid task_id" 
        )
    task = {}
    for val in tasks_db:
        if val["id"] == task_id:
            task = val
    return {
        "task": task
    }

@rouer.get("/tasks/stats")
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

@rouer.get("/tasks/search")
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

@rouer.get("/tasks/status/{status}")
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

# Мы указываем, что эндпоинт будет возвращать данные, 
# соответствующие схеме TaskResponse 
@router.post("/", response_model=TaskResponse, 
status_code=status.HTTP_201_CREATED) 
async def create_task(task: TaskCreate) -> TaskResponse: 
    # Определяем квадрант 
    if task.is_important and task.is_urgent: 
        quadrant = "Q1" 
    elif task.is_important and not task.is_urgent: 
        quadrant = "Q2" 
    elif not task.is_important and task.is_urgent: 
        quadrant = "Q3" 
    else: 
        quadrant = "Q4" 
 
    new_id = max([t["id"] for t in tasks_db], default=0) + 1 # Генерируем новый ID 
    
    new_task = { 
        "id": new_id, 
        "title": task.title, 
        "description": task.description, 
        "is_important": task.is_important, 
        "is_urgent": task.is_urgent, 
        "quadrant": quadrant, 
        "completed": False, 
        "created_at": datetime.now() 
    } 
 
    tasks_db.append(new_task) # "Сохраняем" в нашу "базу данных" 
    
    # Возвращаем созданную задачу (FastAPI автоматически 
    # преобразует dict в Pydantic-модель Task) 
    return new_task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    # ШАГ 1: По аналогии с GET ищем задачу по ID
    task = next(
        (
            task for task in tasks_db
            if task["id"] == task_id
        ),
        None
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # ШАГ 2: Получаем и обновляем только переданные поля (exclude_unset=True)
    # Без exclude_unset=True все None поля тоже попадут в словарь
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        task[field] = value
        
    # ШАГ 3: Пересчитываем квадрант, если изменились важность или срочность
    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"
        else:
            task["quadrant"] = "Q4"
            
    return task

@router.patch("/{task_id}/complete", response_model=TaskResponse) 
async def complete_task(task_id: int) -> TaskResponse: 
    task = next(( 
        task for task in tasks_db 
        if task["id"] == task_id), 
        None 
    ) 
    if not task: 
        raise HTTPException(status_code=404, detail="Задача не найдена") 
    task["completed"] = True 
    task["completed_at"] = datetime.now() 
 
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_task(task_id: int): 
    task = next(( 
        task for task in tasks_db 
        if task["id"] == task_id), 
        None 
    ) 
    if not task: 
        raise HTTPException(status_code=404, detail="Задача не найдена") 
 
    tasks_db.remove(task) 
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    