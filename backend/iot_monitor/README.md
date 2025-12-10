# iotMonitor

FastAPI project to centralize IoT data following the specifications in `backend/specs/01_setup.md`.

## Current Endpoints

- `GET /` – Welcome message.
- `GET /health` – Basic service status.
- `GET /v1/roles/` – List of roles (stored in memory).
- `POST /v1/roles/` – Create a role.
- `GET /v1/roles/{role_id}` – Role details.
- `PUT /v1/roles/{role_id}` – Update a role.
- `DELETE /v1/roles/{role_id}` – Delete a role.
- `GET /v1/users/` – List of active users.
- `POST /v1/users/` – Create a user.
- `GET /v1/users/{user_id}` – User details.
- `PUT /v1/users/{user_id}` – Update a user.
- `DELETE /v1/users/{user_id}` – Logical deletion of a user.
- `POST /v1/iot/data` – IoT readings ingestion.


## Local execution with uv

```bash
cd backend/iot_monitor
~/.local/bin/uv venv --python 3.12      # Create virtual environment (one time only)
source .venv/bin/activate               # Activate environment
uv sync                                 # Install dependencies
uv run uvicorn app.main:app --reload    # Start server at http://127.0.0.1:8000
```

The exposed routes have automatic documentation at `http://127.0.0.1:8000/docs`.
