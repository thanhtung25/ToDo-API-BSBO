# ToDo API (FastAPI)
**ToDo API** — учебный проект для практики работы с **FastAPI**.  
Цель: создать веб-приложение для управления списком задач (To-Do List)  
с классификацией по **матрице Эйзенхауэра** — важность × срочность (Q1–Q4).

---
## ⚙️ Технологии
- Python 3.11
- FastAPI, Uvicorn
---
## 📁 Структура проекта
```
├── Router 
  ├── _init_.py
  ├── stats.py
  └── tasks.py
├── .gitignore # Исключения для Git
├── database.py # Временная база данных (list of dict)
├── main.py # Основная логика приложения (эндпоинты)
├── models.py #  SQLAlchemy модели
├── README.md # Документация проекта
├── requirements.txt # Зависимости проекта
└── schemas.py #  Pydantic модели
```
---
## 🚀 Запуск
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
# или: source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
---
Приложение будет работать по адресу: http://127.0.0.1:8000
Документация Swagger: http://127.0.0.1:8000/docs
---
## Эндпоинты API
- `GET /tasks` - Все задачи
- `GET /tasks/quadrant/{quadrant}` - Фильтр по квадранту (Q1–Q4)
- `GET /tasks/stats` - Общая статистика
- `GET /tasks/status/{status}` - Фильтр по статусу (completed / pending)
- `GET /tasks/search?q=...` - Поиск по ключевому слову
- `GET /tasks/{task_id}` - Получение задачи по ID
---
## Пример статистики 
/tasks/stats:
```bash
curl -s http://127.0.0.1:8000/tasks/stats | python -m json.tool
```
```json
{
  "total_tasks": 4,
  "by_quadrant": {"Q1": 1, "Q2": 1, "Q3": 1, "Q4": 1},
  "by_status": {"completed": 1, "pending": 3}
}
```

/tasks/search: 
```bash
curl -s "http://127.0.0.1:8000/tasks/search?q=API" | python -m json.tool
```
```json
{
  "query": "API",
  "count": 1,
  "tasks": [
    {
      "id": 1,
      "title": "Сдать проект по FastAPI",
      "description": "Завершить разработку API и написать документацию",
      "is_important": true,
      "is_urgent": true,
      "quadrant": "Q1",
      "completed": false
    }
  ]
}
```
