# Sugerencias de Mejoras para el Código

Este documento contiene sugerencias de mejoras pequeñas y prácticas que pueden implementarse en el código para mejorar la calidad, mantenibilidad y robustez del sistema.

## 🔒 Seguridad y Configuración

### 1. **SQLAlchemy echo en producción**
**Ubicación:** `app/db/base.py:10`

**Problema:** `echo=True` está hardcodeado, lo que puede exponer queries SQL en logs de producción.

**Sugerencia:**
```python
# Agregar a Settings
sqlalchemy_echo: bool = False

# En base.py
engine = create_engine(
    settings.database_url, 
    echo=settings.sqlalchemy_echo
)
```

---

### 2. **Pool de conexiones configurable**
**Ubicación:** `app/db/base.py`

**Sugerencia:** Configurar pool de conexiones para mejor manejo de recursos:
```python
engine = create_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=3600,  # Recicla conexiones cada hora
)
```

---

### 3. **Validación de secret_key en producción**
**Ubicación:** `app/core/config.py:25`

**Sugerencia:** Validar que el secret_key no sea el valor por defecto en producción:
```python
def __init__(self):
    super().__init__()
    if self.secret_key == "your-secret-key-change-in-production":
        import os
        if os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY debe cambiarse en producción")
```

---

## 🛡️ Manejo de Errores

### 4. **Rollback explícito en transacciones**
**Ubicación:** `app/iot_data/router.py` y otros routers

**Problema:** No hay rollback explícito cuando ocurren errores en operaciones de base de datos.

**Sugerencia:**
```python
@router.post("/data", response_model=IoTDataRecord, status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    payload: IoTDataIn,
    db: Session = Depends(get_db),
) -> IoTDataRecord:
    try:
        time_data = TimeData(...)
        db.add(time_data)
        db.commit()
        db.refresh(time_data)
        return IoTDataRecord(...)
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing IoT data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al almacenar datos IoT"
        )
```

---

### 5. **Manejo de excepciones de integridad de base de datos**
**Ubicación:** Todos los endpoints POST/PUT

**Sugerencia:** Capturar `IntegrityError` para emails/códigos duplicados:
```python
from sqlalchemy.exc import IntegrityError

try:
    # Operación de base de datos
    db.commit()
except IntegrityError as e:
    db.rollback()
    if "unique constraint" in str(e.orig).lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso ya existe"
        )
    raise
```

---

### 6. **Manejo de excepciones en get_db**
**Ubicación:** `app/db/base.py:19-25`

**Sugerencia:** Mejorar el manejo de errores de conexión:
```python
def get_db():
    """Function for dependency injection of database sessions."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
```

---

## 📝 Validación y Lógica de Negocio

### 7. **Validar email duplicado antes de crear usuario**
**Ubicación:** `app/api/routers/users.py:35-40`

**Sugerencia:** Agregar validación explícita:
```python
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserRead:
    # Validar email duplicado
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )
    return service.create(payload)
```

---

### 8. **Validar estado de dispositivo antes de actualizar**
**Ubicación:** `app/iot_data/router.py:126-151`

**Sugerencia:** Validar que el dispositivo no esté eliminado:
```python
@router.post("/update", response_model=DeviceRegisterRecord, status_code=status.HTTP_200_OK)
def update_device_state(
    payload: DeviceRegisterIn,
    db: Session = Depends(get_db),
) -> DeviceRegisterRecord:
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {payload.device_id} not found",
        )
    
    if device.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="El dispositivo ha sido eliminado",
        )
    
    # ... resto del código
```

---

## 🚀 Performance y Optimización

### 9. **Limpieza periódica del rate limiter**
**Ubicación:** `app/core/rate_limit.py`

**Problema:** El diccionario `_rate_limit_store` puede crecer indefinidamente.

**Sugerencia:** Agregar limpieza periódica de entradas antiguas:
```python
import threading
from datetime import datetime, timedelta, timezone

_cleanup_lock = threading.Lock()

def _cleanup_old_entries():
    """Limpia entradas más antiguas de 1 hora."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=1)
    
    with _cleanup_lock:
        keys_to_delete = [
            key for key, timestamps in _rate_limit_store.items()
            if not timestamps or max(timestamps) < cutoff
        ]
        for key in keys_to_delete:
            del _rate_limit_store[key]

def check_rate_limit(request: Request, key: str | None = None) -> None:
    # ... código existente ...
    
    # Limpiar periódicamente (cada 100 requests aproximadamente)
    if len(_rate_limit_store) > 100:
        _cleanup_old_entries()
```

---

### 10. **Usar bulk insert para múltiples datos IoT**
**Ubicación:** `app/iot_data/router.py:58-95`

**Sugerencia:** Optimizar el bulk insert:
```python
@router.post("/many", response_model=List[IoTDataRecord], status_code=status.HTTP_201_CREATED)
def ingest_many_iot_data(
    payload: List[IoTDataIn],
    db: Session = Depends(get_db),
) -> List[IoTDataRecord]:
    try:
        time_data_list = [
            TimeData(
                id=item.id,
                timestamp=item.timestamp,
                value=item.value,
                unit=item.unit,
                type=item.type,
                sensor_id=item.sensor_id,
                device_id=item.device_id,
            )
            for item in payload
        ]
        
        db.bulk_save_objects(time_data_list)  # Más eficiente que add_all
        db.commit()
        
        # Para obtener los IDs generados, usar bulk_insert_mappings si es necesario
        return [
            IoTDataRecord(
                id=td.id,
                timestamp=td.timestamp,
                value=td.value,
                unit=td.unit,
                type=td.type,
                sensor_id=td.sensor_id,
                device_id=td.device_id,
            )
            for td in time_data_list
        ]
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing multiple IoT data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al almacenar datos IoT"
        )
```

---

## 📊 Logging y Observabilidad

### 11. **Logging estructurado**
**Ubicación:** `app/main.py:13-17`

**Sugerencia:** Usar logging estructurado con contexto:
```python
import logging
import sys
from pythonjsonlogger import jsonlogger  # Agregar a dependencias

# Configurar logger estructurado
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

---

### 12. **Agregar request ID para trazabilidad**
**Ubicación:** Crear middleware nuevo

**Sugerencia:** Crear `app/middleware/request_id.py`:
```python
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

Y agregar en `main.py`:
```python
from app.middleware.request_id import RequestIDMiddleware

app.add_middleware(RequestIDMiddleware)
```

---

## 🔧 Código y Estructura

### 13. **Extraer constantes mágicas**
**Ubicación:** Varios archivos

**Sugerencia:** Crear `app/core/constants.py`:
```python
# Constantes de la aplicación
MAX_BULK_INSERT_SIZE = 1000
RATE_LIMIT_CLEANUP_THRESHOLD = 100
RATE_LIMIT_CLEANUP_HOURS = 1
```

---

### 14. **Usar enum para estados de dispositivo**
**Ubicación:** `app/iot_data/schemas.py:12-18` y `app/db/models/device.py:24`

**Sugerencia:** Ya existe `DeviceState` enum, pero asegurarse de usarlo consistentemente:
```python
# En device.py, usar el enum directamente
from app.iot_data.schemas import DeviceState

state = Column(Enum(DeviceState), nullable=True, default=DeviceState.CREATED)
```

---

### 15. **Validar rango de valores en schemas**
**Ubicación:** `app/iot_data/schemas.py:21-33`

**Sugerencia:** Agregar validaciones de rango:
```python
from pydantic import Field, field_validator

class IoTDataIn(BaseModel):
    value: float = Field(..., ge=-1000, le=1000, description="Valor numérico")
    unit: str | None = Field(None, max_length=20, description="Unidad de medida")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        if v > datetime.now(timezone.utc):
            raise ValueError('El timestamp no puede ser futuro')
        return v
```

---

## 🧪 Testing y Calidad

### 16. **Agregar validación de tipos más estricta**
**Ubicación:** Todos los routers

**Sugerencia:** Usar `Annotated` para dependencias más claras:
```python
from typing import Annotated
from fastapi import Depends

# En lugar de:
def get_user(user_id: UUID, db: Session = Depends(get_db)):

# Usar:
def get_user(
    user_id: UUID, 
    db: Annotated[Session, Depends(get_db)]
):
```

---

### 17. **Documentar códigos de estado HTTP**
**Ubicación:** Todos los routers

**Sugerencia:** Agregar `responses` en decoradores:
```python
@router.post(
    "/data",
    response_model=IoTDataRecord,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Datos almacenados exitosamente"},
        400: {"description": "Datos inválidos"},
        500: {"description": "Error interno del servidor"},
    }
)
```

---

## 🔄 Refactorización Menor

### 18. **Extraer lógica de validación de usuario bloqueado**
**Ubicación:** `app/api/routers/auth.py:28-32`

**Sugerencia:** Ya está bien extraído, pero podría ser un método del modelo:
```python
# En app/db/models/user.py
def is_locked(self) -> bool:
    """Check if user account is locked."""
    if self.locked_until is None:
        return False
    return datetime.now(timezone.utc) < self.locked_until
```

---

### 19. **Consolidar mensajes de error**
**Ubicación:** Varios archivos

**Sugerencia:** Crear `app/core/exceptions.py`:
```python
class ErrorMessages:
    USER_NOT_FOUND = "Usuario no encontrado"
    DEVICE_NOT_FOUND = "Dispositivo no encontrado"
    INVALID_CREDENTIALS = "Email o contraseña incorrectos"
    ACCOUNT_LOCKED = "Cuenta bloqueada"
    # ... más mensajes
```

---

### 20. **Agregar paginación a listados**
**Ubicación:** `app/api/routers/users.py:17-20` y `app/api/routers/roles.py:15-18`

**Sugerencia:** Agregar parámetros de paginación:
```python
from fastapi import Query

@router.get("/", response_model=UserList)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: UserService = Depends(get_user_service)
) -> UserList:
    return service.list(skip=skip, limit=limit)
```

---

## 📦 Dependencias y Configuración

### 21. **Agregar healthcheck más completo**
**Ubicación:** `app/main.py:56-72`

**Sugerencia:** Incluir más información:
```python
@app.get("/health")
def read_health() -> dict[str, Any]:
    """Basic health check endpoint."""
    health_status = {
        "status": "ok",
        "service": settings.project_name,
        "version": settings.version,
        "checks": {}
    }
    
    # Check database
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
        db.close()
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check MQTT
    mqtt_client = get_mqtt_client()
    health_status["checks"]["mqtt"] = {
        "enabled": settings.mqtt_enabled,
        "status": "connected" if mqtt_client._running else "disconnected"
    }
    
    return health_status
```

---

### 22. **Agregar CORS configurable**
**Ubicación:** `app/main.py`

**Sugerencia:** Si la API será consumida desde frontend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 Documentación

### 23. **Agregar ejemplos en schemas**
**Ubicación:** Todos los schemas

**Sugerencia:** Agregar ejemplos para mejor documentación automática:
```python
class IoTDataIn(BaseModel):
    id: UUID = Field(..., description="...", examples=["550e8400-e29b-41d4-a716-446655440000"])
    value: float = Field(..., description="...", examples=[25.5])
    unit: str | None = Field(None, description="...", examples=["°C"])
```

---

## 🎯 Priorización

### Alta Prioridad (Seguridad/Estabilidad)
- ✅ #1: SQLAlchemy echo configurable
- ✅ #4: Rollback explícito
- ✅ #5: Manejo de IntegrityError
- ✅ #3: Validación de secret_key

### Media Prioridad (Mejoras de código)
- ✅ #7: Validar email duplicado
- ✅ #9: Limpieza del rate limiter
- ✅ #11: Logging estructurado
- ✅ #17: Documentar códigos de estado

### Baja Prioridad (Optimizaciones)
- ✅ #10: Bulk insert optimizado
- ✅ #20: Paginación
- ✅ #23: Ejemplos en schemas

---

## 📚 Notas Adicionales

- Estas mejoras son **pequeñas y no requieren refactorización mayor**
- Pueden implementarse **gradualmente** sin romper funcionalidad existente
- Todas son **compatibles con el código actual**
- Considerar **testing** antes de implementar en producción
