FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --exclude=db_storage . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]