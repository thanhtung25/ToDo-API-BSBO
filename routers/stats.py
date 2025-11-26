from fastapi import APIRouter
from database import tasks_db
from typing import Dict

router = APIRouter(
    prefix="/api/v1/stats",
    tags=["stats"]
)

@router.get("")
async def get_stats() -> Dict[str, int]:
    total_tasks = len(tasks_db)
    by_quadrant = {q: 0 for q in ["Q1", "Q2", "Q3", "Q4"]}
    by_status = {"completed": 0, "pending": 0}
    
    for task in tasks_db:
        by_quadrant[task["quadrant"]] += 1
        if task["completed"]:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }
