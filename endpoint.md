# Guía de Endpoints - Panel de Administración

**Versión:** 1.0  
**Propósito:** Documentación de endpoints para implementación del panel de administración  
**Base URL:** `http://localhost:8000/v1` (ajustar según entorno)

---

## 📋 Tabla de Contenidos

- [Autenticación y Sesión](#autenticación-y-sesión)
- [Gestión de Usuarios](#gestión-de-usuarios)
- [Gestión de Roles](#gestión-de-roles)
- [Dashboard y Monitoreo IoT](#dashboard-y-monitoreo-iot)
- [Configuración y Health Checks](#configuración-y-health-checks)

---

## Autenticación y Sesión

### Caso de Uso: Login de Usuario

**Endpoint:** `POST /v1/auth/login`

**Descripción:** Permite a un usuario iniciar sesión en el panel de administración.

**Uso en Panel:**
- Formulario de login
- Validación de credenciales
- Almacenamiento de tokens en localStorage/sessionStorage

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "Password123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores:**
- `401 UNAUTHORIZED`: Credenciales incorrectas
- `423 LOCKED`: Cuenta bloqueada por múltiples intentos fallidos
- `429 TOO_MANY_REQUESTS`: Rate limit excedido

**Notas:**
- Guardar ambos tokens (access y refresh)
- El access_token expira en 30 minutos (configurable)
- El refresh_token expira en 7 días (configurable)
- Implementar rate limiting en el frontend (máx 5 intentos por minuto)

---

### Caso de Uso: Refrescar Token

**Endpoint:** `POST /v1/auth/refresh`

**Descripción:** Renueva el access_token cuando expira sin requerir login nuevamente.

**Uso en Panel:**
- Interceptor HTTP que detecta 401 y refresca automáticamente
- Renovación proactiva antes de que expire
- Mantener sesión activa

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores:**
- `401 UNAUTHORIZED`: Token inválido o revocado

**Notas:**
- El refresh_token anterior se revoca automáticamente
- Guardar el nuevo refresh_token
- Si falla, redirigir al login

---

### Caso de Uso: Cerrar Sesión

**Endpoint:** `POST /v1/auth/logout`

**Descripción:** Cierra la sesión del usuario revocando el refresh token.

**Uso en Panel:**
- Botón de logout
- Limpieza de tokens almacenados
- Redirección al login

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Notas:**
- Limpiar tokens del almacenamiento local
- Invalidate access_token en el cliente (aunque no se revoca en el servidor)

---

## Gestión de Usuarios

### Caso de Uso: Listar Usuarios

**Endpoint:** `GET /v1/users/`

**Descripción:** Obtiene la lista de todos los usuarios activos del sistema.

**Uso en Panel:**
- Tabla de usuarios en página de administración
- Filtrado y búsqueda (implementar en frontend)
- Paginación (preparar para futura implementación)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@example.com",
      "role_id": "123e4567-e89b-12d3-a456-426614174000",
      "password_hash": "$2b$12$...",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "deleted_at": null
    }
  ],
  "total": 1
}
```

**Notas:**
- Solo muestra usuarios activos (deleted_at es null)
- El password_hash no debe mostrarse en el frontend
- Preparar UI para paginación futura

---

### Caso de Uso: Obtener Detalles de Usuario

**Endpoint:** `GET /v1/users/{user_id}`

**Descripción:** Obtiene la información completa de un usuario específico.

**Uso en Panel:**
- Página de detalle de usuario
- Formulario de edición (pre-cargar datos)
- Vista de perfil

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID): ID del usuario

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174000",
  "password_hash": "$2b$12$...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "deleted_at": null
}
```

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado

---

### Caso de Uso: Crear Usuario

**Endpoint:** `POST /v1/users/`

**Descripción:** Crea un nuevo usuario en el sistema.

**Uso en Panel:**
- Formulario de creación de usuario
- Modal de "Nuevo Usuario"
- Validación de contraseña fuerte

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",  // Opcional, se genera automáticamente
  "first_name": "María",
  "last_name": "González",
  "email": "maria@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174000",
  "password": "SecurePass123!"
}
```

**Response (201 CREATED):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "María",
  "last_name": "González",
  "email": "maria@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174000",
  "password_hash": "$2b$12$...",
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "deleted_at": null
}
```

**Validaciones Frontend:**
- Email válido
- Contraseña mínimo 8 caracteres
- Contraseña debe contener: mayúscula, minúscula, número, carácter especial
- Email único (verificar antes de enviar)

**Errores:**
- `400 BAD REQUEST`: Contraseña no cumple requisitos
- `409 CONFLICT`: Email ya existe (si se implementa validación)

---

### Caso de Uso: Actualizar Usuario

**Endpoint:** `PUT /v1/users/{user_id}`

**Descripción:** Actualiza la información de un usuario existente.

**Uso en Panel:**
- Formulario de edición de usuario
- Actualización de perfil
- Cambio de rol de usuario

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID): ID del usuario a actualizar

**Request (campos opcionales, solo enviar los que se actualizan):**
```json
{
  "first_name": "María",
  "last_name": "González López",
  "email": "maria.nueva@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174001",
  "password": "NewSecurePass123!"  // Opcional, solo si se cambia
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "María",
  "last_name": "González López",
  "email": "maria.nueva@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174001",
  "password_hash": "$2b$12$...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:15:00Z",
  "deleted_at": null
}
```

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado
- `400 BAD REQUEST`: Contraseña no cumple requisitos (si se envía)

**Notas:**
- Solo enviar campos que se desean actualizar
- Si se envía password, debe cumplir requisitos de seguridad

---

### Caso de Uso: Eliminar Usuario

**Endpoint:** `DELETE /v1/users/{user_id}`

**Descripción:** Elimina lógicamente un usuario (soft delete).

**Uso en Panel:**
- Botón de eliminar en tabla de usuarios
- Confirmación antes de eliminar
- El usuario desaparece de la lista pero no se borra físicamente

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID): ID del usuario a eliminar

**Response (204 NO CONTENT):** Sin cuerpo

**Errores:**
- `404 NOT FOUND`: Usuario no encontrado

**Notas:**
- Implementar confirmación modal
- Mostrar mensaje de éxito
- Actualizar lista después de eliminar

---

### Caso de Uso: Obtener Usuario Actual

**Endpoint:** `GET /v1/users/me`

**Descripción:** Obtiene la información del usuario autenticado actualmente.

**Uso en Panel:**
- Perfil del usuario actual
- Menú de usuario (nombre, email)
- Verificación de permisos basada en rol

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@example.com",
  "role_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Notas:**
- Llamar al iniciar sesión para obtener datos del usuario
- Usar para mostrar información en header/navbar
- No incluye password_hash (más seguro)

---

## Gestión de Roles

### Caso de Uso: Listar Roles

**Endpoint:** `GET /v1/roles/`

**Descripción:** Obtiene la lista de todos los roles disponibles.

**Uso en Panel:**
- Dropdown/Select para asignar roles a usuarios
- Tabla de roles en página de administración
- Filtrado por nombre

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Administrador",
      "description": "Acceso completo al sistema"
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "name": "Usuario",
      "description": "Acceso básico"
    }
  ],
  "total": 2
}
```

**Notas:**
- Usar para poblar selectores en formularios de usuario
- Cachear en frontend si no cambian frecuentemente

---

### Caso de Uso: Obtener Detalles de Rol

**Endpoint:** `GET /v1/roles/{role_id}`

**Descripción:** Obtiene la información de un rol específico.

**Uso en Panel:**
- Página de detalle de rol
- Formulario de edición de rol

**Path Parameters:**
- `role_id` (UUID): ID del rol

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Administrador",
  "description": "Acceso completo al sistema"
}
```

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

---

### Caso de Uso: Crear Rol

**Endpoint:** `POST /v1/roles/`

**Descripción:** Crea un nuevo rol en el sistema.

**Uso en Panel:**
- Formulario de creación de rol
- Modal "Nuevo Rol"

**Request:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",  // Opcional
  "name": "Editor",
  "description": "Puede editar contenido pero no eliminar"
}
```

**Response (201 CREATED):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "name": "Editor",
  "description": "Puede editar contenido pero no eliminar"
}
```

**Validaciones Frontend:**
- Nombre requerido (mínimo 1 carácter, máximo 100)
- Nombre único (verificar antes de enviar)
- Descripción opcional (máximo 255 caracteres)

---

### Caso de Uso: Actualizar Rol

**Endpoint:** `PUT /v1/roles/{role_id}`

**Descripción:** Actualiza la información de un rol existente.

**Uso en Panel:**
- Formulario de edición de rol
- Actualización de descripción

**Path Parameters:**
- `role_id` (UUID): ID del rol a actualizar

**Request (campos opcionales):**
```json
{
  "name": "Editor Avanzado",
  "description": "Puede editar y eliminar contenido"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "name": "Editor Avanzado",
  "description": "Puede editar y eliminar contenido"
}
```

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

---

### Caso de Uso: Eliminar Rol

**Endpoint:** `DELETE /v1/roles/{role_id}`

**Descripción:** Elimina un rol del sistema.

**Uso en Panel:**
- Botón de eliminar en tabla de roles
- Confirmación antes de eliminar
- Validar que no haya usuarios con ese rol (implementar en frontend)

**Path Parameters:**
- `role_id` (UUID): ID del rol a eliminar

**Response (204 NO CONTENT):** Sin cuerpo

**Errores:**
- `404 NOT FOUND`: Rol no encontrado

**Notas:**
- Verificar usuarios asignados antes de eliminar
- Mostrar advertencia si hay usuarios con ese rol

---

## Dashboard y Monitoreo IoT

### Caso de Uso: Health Check del Sistema IoT

**Endpoint:** `GET /v1/iot/health`

**Descripción:** Verifica el estado de salud del servicio IoT y sus dependencias.

**Uso en Panel:**
- Dashboard principal
- Indicadores de estado del sistema
- Alertas si algún servicio está caído

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "iotMonitor",
  "version": "0.1.0",
  "mqtt": {
    "enabled": true,
    "status": "connected",
    "broker": "localhost:1883",
    "topic": "iot/data"
  },
  "database": "connected"
}
```

**Estados Posibles:**
- `status: "ok"`: Todo funcionando
- `status: "degraded"`: Algún servicio no disponible

**Uso en UI:**
- Mostrar badge verde/amarillo/rojo según estado
- Actualizar cada 30-60 segundos
- Mostrar detalles de MQTT y base de datos

---

### Caso de Uso: Health Check General

**Endpoint:** `GET /health`

**Descripción:** Health check básico del servicio (sin autenticación).

**Uso en Panel:**
- Verificación inicial de conectividad
- Antes de mostrar login
- Monitoreo de disponibilidad

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "iotMonitor",
  "version": "0.1.0",
  "mqtt": {
    "enabled": true,
    "status": "connected",
    "broker": "localhost:1883",
    "topic": "iot/data"
  }
}
```

---

## Configuración y Health Checks

### Caso de Uso: Información del Servicio

**Endpoint:** `GET /`

**Descripción:** Mensaje de bienvenida con información básica.

**Uso en Panel:**
- Página de inicio
- Footer con información del servicio

**Response (200 OK):**
```json
{
  "message": "Welcome to iotMonitor"
}
```

---

## Manejo de Autenticación

### Headers Requeridos

Todos los endpoints protegidos requieren el header de autenticación:

```
Authorization: Bearer <access_token>
```

### Flujo de Autenticación Recomendado

1. **Login inicial:**
   ```javascript
   POST /v1/auth/login
   → Guardar access_token y refresh_token
   ```

2. **En cada request:**
   ```javascript
   Headers: { Authorization: `Bearer ${access_token}` }
   ```

3. **Si recibe 401:**
   ```javascript
   POST /v1/auth/refresh con refresh_token
   → Actualizar access_token
   → Reintentar request original
   ```

4. **Si refresh falla:**
   ```javascript
   → Limpiar tokens
   → Redirigir a login
   ```

### Interceptor HTTP (Ejemplo)

```javascript
// Pseudocódigo para interceptor
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        const newTokens = await refreshToken();
        // Reintentar request original con nuevo token
        return axios.request(error.config);
      } catch {
        // Redirigir a login
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);
```

---

## Códigos de Estado HTTP

| Código | Significado | Acción en Frontend |
|--------|-------------|-------------------|
| `200` | OK | Mostrar datos |
| `201` | Created | Mostrar éxito, actualizar lista |
| `204` | No Content | Mostrar éxito, actualizar lista |
| `400` | Bad Request | Mostrar errores de validación |
| `401` | Unauthorized | Refrescar token o redirigir a login |
| `404` | Not Found | Mostrar "Recurso no encontrado" |
| `409` | Conflict | Mostrar "Ya existe" |
| `423` | Locked | Mostrar "Cuenta bloqueada" |
| `429` | Too Many Requests | Mostrar "Demasiados intentos, esperar" |
| `500` | Internal Server Error | Mostrar "Error del servidor" |

---

## Estructura de Datos Comunes

### UUID
Formato estándar: `550e8400-e29b-41d4-a716-446655440000`

### Timestamp
Formato ISO 8601 UTC: `2024-01-15T10:30:00Z`

### Paginación (Futuro)
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

---

## Notas de Implementación

### Validaciones Frontend

1. **Email:**
   - Formato válido
   - Verificar unicidad antes de crear/actualizar

2. **Contraseña:**
   - Mínimo 8 caracteres
   - Al menos: mayúscula, minúscula, número, carácter especial
   - Validar antes de enviar

3. **UUIDs:**
   - Validar formato antes de enviar
   - Generar en frontend si es necesario

### Manejo de Errores

- Mostrar mensajes de error amigables
- Logging de errores para debugging
- Retry automático para errores de red
- Timeout configurado (ej: 30 segundos)

### Performance

- Cachear listas de roles (cambian poco)
- Implementar debounce en búsquedas
- Lazy loading de datos grandes
- Optimistic updates donde sea posible

### Seguridad

- No almacenar tokens en localStorage si es posible (usar httpOnly cookies en futuro)
- Limpiar tokens al cerrar sesión
- Validar permisos en frontend (pero confiar en backend)
- No mostrar información sensible (password_hash)

---

## Endpoints No Documentados (Futuros)

Los siguientes endpoints están en desarrollo o planeados:

- `GET /v1/iot/data` - Consultar datos IoT (con filtros)
- `GET /v1/devices/` - Listar dispositivos
- `GET /v1/sensors/` - Listar sensores
- `GET /v1/businesses/` - Gestión de empresas
- `GET /v1/branches/` - Gestión de sucursales
- `GET /v1/machines/` - Gestión de máquinas
- `GET /v1/reports/` - Generación de reportes

---

**Última actualización:** 2024  
**Mantenido por:** Equipo iotMonitor
