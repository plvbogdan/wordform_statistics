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
ru, en, de, fr, es, it, pt, nl, pl, cs, sk, da, sv, no, fi, hu, tr, uk, bg, sr, hr, sl, el, 
ro, et, lv, lt, ca, gl, eu, ga, gd, cy, is, lb, mt, id, ms, tl, sw, hi, fa, la 


Библиотека simplemma поддерживает все эти языки. В рамках выполнения задания была протестирована работа 
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
