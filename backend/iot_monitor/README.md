# iotMonitor

FastAPI project to centralize IoT data following the specifications in `backend/specs/01_setup.md`.

## Current Endpoints

- `GET /` – Welcome message.
- `GET /health` – Basic service status.
- `POST /v1/auth/login` – Login and get access/refresh tokens.
- `POST /v1/auth/refresh` – Refresh access token.
- `POST /v1/auth/logout` – Revoke refresh token (logout).
- `GET /v1/roles/` – List roles.
- `POST /v1/roles/` – Create a role.
- `GET /v1/roles/{role_id}` – Role details.
- `PUT /v1/roles/{role_id}` – Update a role.
- `DELETE /v1/roles/{role_id}` – Delete a role.
- `GET /v1/users/` – List active users.
- `POST /v1/users/` – Create a user.
- `GET /v1/users/{user_id}` – User details.
- `PUT /v1/users/{user_id}` – Update a user.
- `DELETE /v1/users/{user_id}` – Logical deletion of a user.
- `GET /v1/users/me` – Current user info (requires access token).
- `POST /v1/iot/data` – IoT readings ingestion.
- `POST /v1/iot/many` – Bulk IoT readings ingestion.
- `POST /v1/iot/register` – Register device state.
- `POST /v1/iot/update` – Update device state.
- `GET /v1/iot/health` – IoT gateway health check.

Note: Only `GET /v1/users/me` enforces authentication at the moment.


## Local execution with uv

```bash
cd backend/iot_monitor
~/.local/bin/uv venv --python 3.11      # Create virtual environment (one time only)
source .venv/bin/activate               # Activate environment
uv sync                                 # Install dependencies
uv run uvicorn app.main:app --reload    # Start server at http://127.0.0.1:8000
```

The exposed routes have automatic documentation at `http://127.0.0.1:8000/docs`.
