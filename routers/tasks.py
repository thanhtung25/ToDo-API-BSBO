from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime

router= APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"decription" : "Task not found"}},
)

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
@router.get("")
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
@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for t in tasks_db:
        if t.get("id") == task_id:
            return t
    raise HTTPException(status_code=404, detail="Задача не найдена")