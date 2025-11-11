# 📝 ToDo-API-BSBO

Небольшое учебное API на **FastAPI** для работы со списком задач по матрице Эйзенхауэра.

---

## 🚀 Возможности

- Просмотр всех задач  
- Поиск по названию и описанию  
- Фильтрация по квадрантам (Q1–Q4)  
- Отбор по статусу (`completed` / `pending`)  
- Получение статистики  

---

## ⚙️ Установка и запуск

```bash
git clone https://github.com/yourusername/ToDo-API-BSBO.git
cd ToDo-API-BSBO
python -m venv venv
source venv/bin/activate   # или venv\Scripts\activate на Windows
pip install fastapi uvicorn
uvicorn main:app --reload
