from fastapi import APIRouter, HTTPException, Query, status, Response
from typing import List, Dict, Any
from datetime import datetime
from schemas import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from database import tasks_db

router= APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"decription" : "Task not found"}},
)

@router.get("", response_model=Dict[str, Any])
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),
        "tasks": tasks_db
    }

# =================== B. КОНКРЕТНЫЕ МАРШРУТЫ (ПРЕДПОЧТИТЕЛЬНЫЕ) ==================

# 1) /tasks/stats — общая статистика, по квадрантам, по статусу (completed/pending)
@router.get("/stats")
async def get_tasks_stats() -> dict:
    total = len(tasks_db)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for t in tasks_db:
        q = t.get("quadrant")
        if q in by_quadrant:
            by_quadrant[q] += 1

    completed_cnt = sum(1 for t in tasks_db if t.get("completed") is True)
    pending_cnt = total - completed_cnt
    by_status = {"completed": completed_cnt, "pending": pending_cnt}

    return {"total_tasks": total, "by_quadrant": by_quadrant, "by_status": by_status}

# 2) /tasks/search?q=... — поиск по ключевому слову в title/description (>=2 символов)
@router.get("/search")
async def search_tasks(q: str) -> dict:
    if q is None or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Ключевое слово должно содержать минимум 2 символа")

    kw = q.strip().lower()
    matched = [
        t for t in tasks_db
        if (t.get("title") and kw in t["title"].lower())
        or (t.get("description") and kw in t["description"].lower())
    ]

    if not matched:
        # Согласно запросу поста: вернуть 404, если нет результатов
        raise HTTPException(status_code=404, detail="Задачи по данному запросу не найдены")

    return {"query": q, "count": len(matched), "tasks": matched}

# 3) /tasks/status/{status} — фильтр по статусу: completed | pending
@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    allowed = {"completed", "pending"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail='Недопустимый статус. Используйте: "completed" или "pending"')

    target = True if status == "completed" else False
    filtered = [t for t in tasks_db if t.get("completed") is target]

    if not filtered:
        raise HTTPException(status_code=404, detail="Задачи с данным статусом не найдены")

    return {"status": status, "count": len(filtered), "tasks": filtered}
# ================== C. Общие маршруты ==================

# /tasks/quadrant/{quadrant} — матричная фильтрация Eisenhower
@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    allowed = {"Q1", "Q2", "Q3", "Q4"}
    if quadrant not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    filtered_tasks = [task for task in tasks_db if task.get("quadrant") == quadrant]
    return {"quadrant": quadrant, "count": len(filtered_tasks), "tasks": filtered_tasks}

# ================== D. ДИНАМИЧЕСКИЙ МАРШРУТ (УСТАНОВЛЕН ПОСЛЕДНИМ)==================
# 4) /tasks/{task_id} — брать ID
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    if task.is_important and task.is_urgent:
        quadrant = "Q1"
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"
    else:
        quadrant = "Q4"
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
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
    tasks_db.append(new_task)
    return new_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value
    
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
async def complete_task(task_id: int):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task["completed"] = True
    task["completed_at"] = datetime.now()
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)