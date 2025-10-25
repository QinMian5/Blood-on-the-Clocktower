# syntax=docker/dockerfile:1

FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY --from=frontend /app/frontend/dist ./frontend/dist
ENV APP_ENV=prod
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
