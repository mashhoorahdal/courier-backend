# syntax = docker/dockerfile:1.5
ARG PYTHON_VERSION="3.12"

FROM python:${PYTHON_VERSION}-slim AS build

# Install system deps (for psycopg2 + uv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy the Django project
COPY . .

# Expose Django port
EXPOSE 8000

# Set Django environment variables
ENV DJANGO_SETTINGS_MODULE=courier_backend.settings
ENV PYTHONUNBUFFERED=1

CMD ["bash", "-c", "python manage.py migrate && gunicorn courier_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3"]
