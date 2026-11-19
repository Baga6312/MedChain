FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root application user
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Copy application files with correct ownership
COPY --chown=django:django . .

# Create media directory and assign ownership
RUN mkdir -p /app/media/avatars /app/logs \
    && chown -R django:django /app/media /app/logs \
    && chmod -R 755 /app/media \
    && chmod 0777 /app/logs

# Run as non-root user
USER django

EXPOSE 8000

CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${BACKEND_PORT:-8000} --worker-tmp-dir /dev/shm"]
