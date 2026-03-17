# WordForm Counter API


## Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/plvbogdan/wordform_statistics.git
cd wordform_statistics
```
### 2.Создание виртуального окружения и установка зависимостей
```bash
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

### 3.Запуск
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4.Работа с приложением
1. После запуска необходимо открыть в браузере
Swagger UI: http://localhost:8000/docs

2. Выбрать файл для сбора статистики: file

3. Выбрать язык, на котором написан текст в файле: language

4. После отправки файла вы получите task_id, по которому вы можете получить статус задачи и загрузить файл при его успешной обработке

