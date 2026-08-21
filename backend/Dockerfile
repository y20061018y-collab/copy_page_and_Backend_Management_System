FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN mkdir -p uploads/games uploads/studio
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && python -m app.seed_admin && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
