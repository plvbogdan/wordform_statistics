from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from models import Task
from counter import count_words
from utils import save_to_excel
import uuid
import asyncio
import os

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

DESCRIPTION = """
WordForm Counter API

**Поддерживаемые языки:**

Библиотека simplemma поддерживает ast, bg, ca, cs, cy, da, de, el, en, enm, es, 
et, fa, fi, fr, ga, gd, gl, gv, hbs, hi, hu, hy, id, is, it, ka, la, lb, lt, lv, 
mk, ms, nb, nl, nn, pl, pt, ro, ru, se, sk, sl, sq, sv, sw, tl, tr, uk языки.

В рамках выполнения задания была протестирована работа 
библиотеки с английским (en), немецким (de) и французским (fr) языками

Для работы с русским языком используется pymorphy3 для повышения точности лемматизации
"""
app = FastAPI(
    title="WordForm Counter",
    description=DESCRIPTION
)



tasks = {}
queue = []
TEMP_DIR = "temp"

@app.post("/public/report/export")
async def export(
    file: UploadFile = File(None, description="Текстовый файл для анализа"),
    task_id: str = Form('', description="ID задачи для получения результата"),
    language: str = Form('ru', description="Код языка (см. список в документации)")
):
    
    if task_id:
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(404, "Задача не найдена")
        
        if task.status == "completed":
            return FileResponse(
                task.result_path,
                filename=f"result_{task_id}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        return {
            "task_id": task_id,
            "status": task.status,  
            "progress": task.progress,
            "queue_position": queue.index(task_id) + 1 if task_id in queue else 0,
            "error": task.error
        }
    
    if not file:
        raise HTTPException(400, "Укажите task_id или файл")
    
    content = await file.read()

    task = Task(
        id=str(uuid.uuid4()),
        language=language,
        result_path=f"{TEMP_DIR}/result_{uuid.uuid4()}.xlsx"
    )

    tasks[task.id] = task
    queue.append(task.id)

    asyncio.create_task(process_file(task.id, content))

    return {
        "task_id": task.id,
        "status": "pending",
        "queue_position": len(queue),
        "message": f"Файл принят. Используйте этот task_id для получения результата."
    }


async def process_file(task_id: str, content: bytes):
    task = tasks[task_id]
    task.status = "processing"

    try: 

        async def update_progress(p: int):
            task.progress = p

        stats = await count_words(content, task.language, update_progress)

        save_to_excel(stats, task.result_path)
        task.status = "completed"
        task.progress = 100
    
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
    finally:
        if task_id in queue:
            queue.remove(task_id)
