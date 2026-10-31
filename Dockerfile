# 1. Imagen base: Python ligero (espejo de Docker Hub en ECR Public: evita el límite de descargas en CodeBuild)
FROM public.ecr.aws/docker/library/python:3.12-slim

# 2. Metadatos de versión inyectados por CodeBuild (visibles en /health)
ARG APP_VERSION=1.0.0
ARG COMMIT_SHA=local

# 3. Variables de entorno: sin .pyc, logs sin buffer, versión y BD
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION} \
    COMMIT_SHA=${COMMIT_SHA} \
    APP_ENV=production \
    DATABASE_URL=sqlite:////code/data/estudiantes.db

# 4. Directorio de trabajo
WORKDIR /code

# 5. Dependencias (capa cacheada si requirements.txt no cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Código fuente de la API
COPY app ./app

# 7. Usuario sin privilegios y carpeta de datos (SQLite) con permisos de escritura
RUN useradd --uid 10001 --create-home appuser && mkdir -p /code/data && chown -R appuser:appuser /code/data
USER appuser

# 8. Puerto y health check del contenedor
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"

# 9. Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
