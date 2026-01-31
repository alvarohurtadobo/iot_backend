# Documentación de Endpoints - IoT Backend

Esta documentación resume todos los endpoints disponibles en la API del sistema IoT.

## Base URL

Todos los endpoints de la API v1 están bajo el prefijo `/v1`, excepto los endpoints raíz.

---

## 🔐 Autenticación (`/v1/auth`)

### POST `/v1/auth/login`
Inicia sesión y obtiene tokens de acceso y actualización.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Características:**
- Rate limiting por email
- Bloqueo de cuenta después de múltiples intentos fallidos
- Auditoría de intentos de inicio de sesión
- Validación de cuenta bloqueada o deshabilitada

**Errores comunes:**
- `401 UNAUTHORIZED`: Credenciales inválidas o cuenta deshabilitada
- `423 LOCKED`: Cuenta bloqueada temporalmente
- `429 TOO_MANY_REQUESTS`: Rate limit excedido

---

### POST `/v1/auth/refresh`
Refresca el token de acceso usando el token de actualización.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Nota:** El token de actualización anterior se revoca automáticamente.

**Errores comunes:**
- `401 UNAUTHORIZED`: Token inválido, revocado o usuario deshabilitado

---

### POST `/v1/auth/logout`
Cierra sesión revocando el token de actualización.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:** `200 OK`
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Nota:** Si el token ya es inválido o fue revocado, el endpoint igualmente responde `200 OK`.

---

## 👥 Usuarios (`/v1/users`)

**Autenticación requerida:** No (solo `/v1/users/me` requiere access token)

### GET `/v1/users/`
Lista todos los usuarios activos.

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 0
}
```

---

### GET `/v1/users/{user_id}`
Obtiene la información detallada de un usuario por su ID.

**Path Parameters:**
- `user_id` (UUID): Identificador único del usuario

**Response:** `200 OK` - Objeto `UserRead`

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado

---

### POST `/v1/users/`
Crea un nuevo usuario.

**Request Body:** `UserCreate`

**Response:** `201 CREATED` - Objeto `UserRead`

---

### PUT `/v1/users/{user_id}`
Actualiza la información de un usuario existente.

**Path Parameters:**
- `user_id` (UUID): Identificador único del usuario

**Request Body:** `UserUpdate`

**Response:** `200 OK` - Objeto `UserRead`

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado

---

### DELETE `/v1/users/{user_id}`
Elimina lógicamente un usuario (soft delete).

**Path Parameters:**
- `user_id` (UUID): Identificador único del usuario

**Response:** `204 NO CONTENT`

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado

---

### GET `/v1/users/me`
Obtiene la información del usuario autenticado actualmente.

**Autenticación requerida:** Sí

**Response:** `200 OK` - Objeto `UserPublic`

**Errores:**
- `401 UNAUTHORIZED`: Token inválido, revocado o usuario deshabilitado

---

## 🎭 Roles (`/v1/roles`)

**Autenticación requerida:** No

### GET `/v1/roles/`
Lista todos los roles disponibles.

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 0
}
```

---

### GET `/v1/roles/{role_id}`
Obtiene la información de un rol por su ID.

**Path Parameters:**
- `role_id` (UUID): Identificador único del rol

**Response:** `200 OK` - Objeto `RoleRead`

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

---

### POST `/v1/roles/`
Crea un nuevo rol.

**Request Body:** `RoleCreate`

**Response:** `201 CREATED` - Objeto `RoleRead`

---

### PUT `/v1/roles/{role_id}`
Actualiza un rol existente.

**Path Parameters:**
- `role_id` (UUID): Identificador único del rol

**Request Body:** `RoleUpdate`

**Response:** `200 OK` - Objeto `RoleRead`

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

---

### DELETE `/v1/roles/{role_id}`
Elimina un rol.

**Path Parameters:**
- `role_id` (UUID): Identificador único del rol

**Response:** `204 NO CONTENT`

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

---

## 📡 IoT (`/v1/iot`)

### POST `/v1/iot/data`
Recibe y almacena una lectura de un dispositivo IoT.

**Request Body:**
```json
{
  "id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "value": 25.5,
  "unit": "°C",
  "type": "double",
  "sensor_id": "uuid",
  "device_id": "uuid"
}
```

**Response:** `201 CREATED` - Objeto `IoTDataRecord`

---

### POST `/v1/iot/many`
Recibe y almacena múltiples lecturas de dispositivos IoT en una sola operación.

**Request Body:** Array de `IoTDataIn`
```json
[
  {
    "id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z",
    "value": 25.5,
    "unit": "°C",
    "type": "double",
    "sensor_id": "uuid",
    "device_id": "uuid"
  },
  ...
]
```

**Response:** `201 CREATED` - Array de `IoTDataRecord`

---

### POST `/v1/iot/register`
Registra el estado de un dispositivo IoT.

**Request Body:**
```json
{
  "device_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "state": "active"
}
```

**Estados disponibles:** `created`, `active`, `disabled`, `error`

**Response:** `200 OK` - Objeto `DeviceRegisterRecord`

**Errores:**
- `404 NOT FOUND`: Dispositivo no encontrado

---

### POST `/v1/iot/update`
Actualiza el estado de un dispositivo IoT.

**Request Body:**
```json
{
  "device_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "state": "active"
}
```

**Estados disponibles:** `created`, `active`, `disabled`, `error`

**Response:** `200 OK` - Objeto `DeviceRegisterRecord`

**Errores:**
- `404 NOT FOUND`: Dispositivo no encontrado

---

### GET `/v1/iot/health`
Verifica el estado de salud del servicio IoT gateway.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "string",
  "version": "string",
  "mqtt": {
    "enabled": true,
    "status": "connected",
    "broker": "host:port",
    "topic": "string"
  },
  "database": "connected"
}
```

**Estados posibles:**
- `ok`: Todo funcionando correctamente
- `degraded`: Algún servicio no está disponible

---

## 🏠 Endpoints Raíz

### GET `/`
Mensaje de bienvenida de la API.

**Response:** `200 OK`
```json
{
  "message": "Welcome to iotMonitor"
}
```

---

### GET `/health`
Health check básico del servicio.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "string",
  "version": "string",
  "mqtt": {
    "enabled": true,
    "status": "connected",
    "broker": "host:port",
    "topic": "string"
  }
}
```

---

## 🔒 Autenticación

La mayoría de los endpoints requieren autenticación mediante JWT Bearer Token. Para autenticarse:

1. Obtén un token usando `POST /v1/auth/login`
2. Incluye el token en el header de las peticiones:
   ```
   Authorization: Bearer <access_token>
   ```
3. Si el token expira, usa `POST /v1/auth/refresh` para obtener uno nuevo

---

## 📝 Notas

- Todos los UUIDs deben estar en formato estándar (ej: `550e8400-e29b-41d4-a716-446655440000`)
- Las fechas deben estar en formato ISO 8601 (ej: `2024-01-01T00:00:00Z`)
- Los endpoints de IoT no requieren autenticación por defecto (pueden ser configurados según necesidades de seguridad)
- El sistema implementa rate limiting en el endpoint de login para prevenir ataques de fuerza bruta
- Los usuarios eliminados se marcan como `deleted_at` (soft delete) y no aparecen en las listas
