# API de Estudiantes · CI/CD con AWS CodePipeline

FastAPI + SQLAlchemy en Docker, desplegada automáticamente:
GitHub → CodePipeline → CodeBuild (pytest + docker build + push a ECR) → Elastic Beanstalk (Docker, AL2023).

## Estructura
```
app/main.py                    # entrada FastAPI (uvicorn app.main:app)
app/config.py, database.py     # configuración por entorno y SQLAlchemy
app/models.py, schemas.py      # Modelo ORM y DTOs validados (Pydantic)
app/repositories/              # acceso a datos
app/services/                  # reglas de negocio (correo único, 404)
app/routers/students.py        # controlador REST
app/errors.py                  # errores de dominio → HTTP
tests/                         # 17 pruebas (pytest, BD en memoria)
Dockerfile                     # usuario sin privilegios + HEALTHCHECK
buildspec.yml                  # CodeBuild: prueba, construye, publica en ECR
deploy/Dockerrun.aws.json.template  # descriptor de Beanstalk (CodeBuild pone la imagen)
deploy/.ebextensions/          # health check /health y carpeta de datos
VERSION                        # versión visible en /health
```

## Endpoints
| Método | Ruta | Respuesta |
|---|---|---|
| POST | /students | 201 creado · 409 correo duplicado · 422 datos inválidos |
| GET | /students?skip=0&limit=50 | lista + cabecera `X-Total-Count` |
| GET | /students/{id} | 200 · 404 |
| PUT | /students/{id} | actualización parcial |
| DELETE | /students/{id} | 204 |
| GET | /health | estado y versión desplegada |
| GET | /docs | Swagger UI |

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
docker build -t api-estudiantes . && docker run -d -p 8000:8000 --name api-est api-estudiantes
curl -X POST localhost:8000/students -H "Content-Type: application/json" \
     -d '{"nombre":"Ana","apellido":"Garcia","correo":"ana@uni.edu"}'
curl localhost:8000/students
```

## Probar el pipeline
1. Cambia `VERSION` a `1.1.0`.
2. `git commit -am "feat: version 1.1.0" && git push`
3. Al terminar: `curl http://<url-beanstalk>/health` → `"version":"1.1.0+<commit>"`.
