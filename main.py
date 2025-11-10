# main.py
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo API",
    version="1.0",
    contact={"name": "Нгуен Кхак Тхань Тунг"},
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

@app.get("/")
async def welcome() -> dict:
    return {"message": "Привет, студент!"}

# ================== B. ROUTES CỤ THỂ (ĐẶT TRƯỚC) ==================

# 1) /tasks/stats — thống kê tổng, theo quadrant, theo trạng thái (completed/pending)
@app.get("/tasks/stats")
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

# 2) /tasks/search?q=... — tìm theo từ khóa trong title/description (>=2 ký tự)
@app.get("/tasks/search")
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
        # Theo yêu cầu bài: trả 404 nếu không có kết quả
        raise HTTPException(status_code=404, detail="Задачи по данному запросу не найдены")

    return {"query": q, "count": len(matched), "tasks": matched}

# 3) /tasks/status/{status} — lọc theo trạng thái: completed | pending
@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    allowed = {"completed", "pending"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail='Недопустимый статус. Используйте: "completed" или "pending"')

    target = True if status == "completed" else False
    filtered = [t for t in tasks_db if t.get("completed") is target]

    if not filtered:
        raise HTTPException(status_code=404, detail="Задачи с данным статусом не найдены")

    return {"status": status, "count": len(filtered), "tasks": filtered}
# ================== C. ROUTES CHUNG ==================
# /tasks — tất cả task
@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}
# /tasks/quadrant/{quadrant} — lọc theo ma trận Eisenhower
@app.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    allowed = {"Q1", "Q2", "Q3", "Q4"}
    if quadrant not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    filtered_tasks = [task for task in tasks_db if task.get("quadrant") == quadrant]
    return {"quadrant": quadrant, "count": len(filtered_tasks), "tasks": filtered_tasks}

# ================== D. ROUTE ĐỘNG (ĐẶT SAU CÙNG) ==================
# 4) /tasks/{task_id} — lấy theo ID
@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for t in tasks_db:
        if t.get("id") == task_id:
            return t
    raise HTTPException(status_code=404, detail="Задача не найдена")