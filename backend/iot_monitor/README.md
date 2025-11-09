# iotMonitor

Proyecto FastAPI para centralizar datos IoT siguiendo las especificaciones de `backend/specs/01_setup.md`.

## Endpoints actuales

- `GET /` – Mensaje de bienvenida.
- `GET /health` – Estado básico del servicio.
- `GET /v1/roles/` – Listado de roles (almacenados en memoria).
- `POST /v1/roles/` – Crear un role.
- `GET /v1/roles/{role_id}` – Detalle de un role.
- `PUT /v1/roles/{role_id}` – Actualizar un role.
- `DELETE /v1/roles/{role_id}` – Eliminar un role.
- `GET /v1/users/` – Listado de usuarios activos.
- `POST /v1/users/` – Crear un usuario.
- `GET /v1/users/{user_id}` – Detalle de un usuario.
- `PUT /v1/users/{user_id}` – Actualizar un usuario.
- `DELETE /v1/users/{user_id}` – Borrado lógico de un usuario.

## Ejecución local con uv

```bash
cd backend/iot_monitor
~/.local/bin/uv venv --python 3.12      # Crear entorno virtual (una sola vez)
source .venv/bin/activate               # Activar entorno
uv sync                                 # Instalar dependencias
uv run uvicorn app.main:app --reload    # Levantar servidor en http://127.0.0.1:8000
```

Las rutas expuestas cuentan con documentación automática en `http://127.0.0.1:8000/docs`.
