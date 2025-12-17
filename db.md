# Documentación de Base de Datos - IoT Backend

Este documento contiene un resumen gráfico de todas las tablas de la base de datos, sus campos y tipos de datos.

## 📊 Diagrama de Relaciones

```
┌─────────────┐
│  Business   │
│  (Empresa)  │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐    ┌─────────────┐
│   Branch    │    │   Machine   │
│  (Sucursal) │    │  (Máquina)  │
└──────┬──────┘    └──────┬───────┘
       │                 │
       │                 │
       ▼                 ▼
┌─────────────┐    ┌─────────────┐
│    User     │    │   Device    │
│  (Usuario)  │    │ (Dispositivo)│
└──────┬──────┘    └──────┬───────┘
       │                  │
       │                  │
       │                  ▼
       │            ┌─────────────┐
       │            │   Sensor    │
       │            │  (Sensor)   │
       │            └──────┬───────┘
       │                  │
       │                  ▼
       │            ┌─────────────┐
       │            │  TimeData   │
       │            │ (Datos IoT) │
       │            └─────────────┘
       │
       ▼
┌─────────────┐
│ LoginAudit │
│ (Auditoría)│
└─────────────┘

┌─────────────┐
│   Role      │
│  (Rol)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    User     │
└─────────────┘

┌─────────────┐
│RevokedToken │
│(Token Rev.) │
└─────────────┘

┌─────────────┐
│ DeviceType  │
│(Tipo Dispo.)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Device    │
└─────────────┘

┌─────────────┐
│ SensorType  │
│(Tipo Sensor)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Sensor    │
└─────────────┘

┌─────────────┐      ┌─────────────┐
│   Report    │◄────►│  TimeData   │
│  (Reporte)  │      │ (Datos IoT) │
└──────┬──────┘      └─────────────┘
       │
       │ (relaciona con: Business, Branch, Machine, Device)
```

---

## 📋 Tablas Detalladas

### 1. `businesses` - Empresas

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre de la empresa |
| `description` | TEXT | NULL | Descripción de la empresa |
| `picture_url` | VARCHAR(500) | NULL | URL de la imagen de la empresa |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |

**Relaciones:**
- `branches` (1:N) - Una empresa tiene muchas sucursales
- `machines` (1:N) - Una empresa tiene muchas máquinas
- `users` (1:N) - Una empresa tiene muchos usuarios
- `reports` (1:N) - Una empresa tiene muchos reportes

---

### 2. `branches` - Sucursales

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre de la sucursal |
| `description` | TEXT | NULL | Descripción de la sucursal |
| `business_id` | UUID | FOREIGN KEY → businesses.id, NOT NULL, INDEX | ID de la empresa |
| `representative_id` | UUID | FOREIGN KEY → users.id, NULL | ID del representante/usuario |
| `address` | VARCHAR(500) | NULL | Dirección de la sucursal |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |

**Relaciones:**
- `business` (N:1) - Pertenece a una empresa
- `representative` (N:1) - Tiene un representante (usuario)
- `users` (1:N) - Una sucursal tiene muchos usuarios
- `machines` (1:N) - Una sucursal tiene muchas máquinas
- `reports` (1:N) - Una sucursal tiene muchos reportes

---

### 3. `roles` - Roles

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE | Nombre del rol |
| `description` | TEXT | NULL | Descripción del rol |

**Relaciones:**
- `users` (1:N) - Un rol tiene muchos usuarios

---

### 4. `users` - Usuarios

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `first_name` | VARCHAR(255) | NOT NULL | Nombre del usuario |
| `last_name` | VARCHAR(255) | NOT NULL | Apellido del usuario |
| `profile_picture` | VARCHAR(500) | NULL | URL de la foto de perfil |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | Email del usuario |
| `password` | VARCHAR(255) | NOT NULL | Hash de la contraseña |
| `role_id` | UUID | FOREIGN KEY → roles.id, NOT NULL | ID del rol |
| `business_id` | UUID | FOREIGN KEY → businesses.id, NULL | ID de la empresa |
| `branch_id` | UUID | FOREIGN KEY → branches.id, NULL | ID de la sucursal |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |
| `failed_login_attempts` | VARCHAR(10) | NOT NULL, DEFAULT '0' | Intentos fallidos de login |
| `locked_until` | TIMESTAMP WITH TIME ZONE | NULL | Fecha hasta la cual la cuenta está bloqueada |
| `last_login_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha del último login exitoso |

**Relaciones:**
- `role` (N:1) - Pertenece a un rol
- `business` (N:1) - Pertenece a una empresa (opcional)
- `branch` (N:1) - Pertenece a una sucursal (opcional)
- `branches_as_representative` (1:N) - Puede ser representante de varias sucursales

---

### 5. `machines` - Máquinas

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre de la máquina |
| `code` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Código único de la máquina |
| `description` | TEXT | NULL | Descripción de la máquina |
| `business_id` | UUID | FOREIGN KEY → businesses.id, NOT NULL, INDEX | ID de la empresa |
| `branch_id` | UUID | FOREIGN KEY → branches.id, NOT NULL, INDEX | ID de la sucursal |
| `year` | INTEGER | NULL | Año de fabricación |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |

**Relaciones:**
- `business` (N:1) - Pertenece a una empresa
- `branch` (N:1) - Pertenece a una sucursal
- `devices` (1:N) - Una máquina tiene muchos dispositivos
- `sensors` (1:N) - Una máquina tiene muchos sensores
- `reports` (1:N) - Una máquina tiene muchos reportes

---

### 6. `device_types` - Tipos de Dispositivos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre del tipo |
| `code` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Código único del tipo |

**Relaciones:**
- `devices` (1:N) - Un tipo tiene muchos dispositivos

---

### 7. `devices` - Dispositivos IoT

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre del dispositivo |
| `code` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Código único del dispositivo |
| `description` | TEXT | NULL | Descripción del dispositivo |
| `type_id` | UUID | FOREIGN KEY → device_types.id, NOT NULL, INDEX | ID del tipo de dispositivo |
| `machine_id` | UUID | FOREIGN KEY → machines.id, NOT NULL, INDEX | ID de la máquina |
| `location` | VARCHAR(500) | NULL | Ubicación del dispositivo |
| `state` | VARCHAR(20) | NULL | Estado: 'created', 'active', 'disabled', 'error' |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |

**Relaciones:**
- `device_type` (N:1) - Pertenece a un tipo de dispositivo
- `machine` (N:1) - Pertenece a una máquina
- `sensors` (1:N) - Un dispositivo tiene muchos sensores
- `time_data` (1:N) - Un dispositivo genera muchos datos temporales
- `reports` (1:N) - Un dispositivo tiene muchos reportes

---

### 8. `sensor_types` - Tipos de Sensores

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre del tipo de sensor |
| `code` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Código único del tipo |
| `type` | VARCHAR(50) | NOT NULL | Tipo de dato: 'double', 'int', etc. |

**Relaciones:**
- `sensors` (1:N) - Un tipo tiene muchos sensores

---

### 9. `sensors` - Sensores

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre del sensor |
| `type_id` | UUID | FOREIGN KEY → sensor_types.id, NOT NULL, INDEX | ID del tipo de sensor |
| `device_id` | UUID | FOREIGN KEY → devices.id, NOT NULL, INDEX | ID del dispositivo |
| `machine_id` | UUID | FOREIGN KEY → machines.id, NOT NULL, INDEX | ID de la máquina |

**Relaciones:**
- `sensor_type` (N:1) - Pertenece a un tipo de sensor
- `device` (N:1) - Pertenece a un dispositivo
- `machine` (N:1) - Pertenece a una máquina
- `time_data` (1:N) - Un sensor genera muchos datos temporales

---

### 10. `time_data` - Datos Temporales IoT

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NOT NULL, INDEX | Timestamp de la lectura |
| `value` | FLOAT | NOT NULL | Valor numérico de la lectura |
| `unit` | VARCHAR(50) | NULL | Unidad de medida (ej: '°C', 'kPa') |
| `type` | VARCHAR(50) | NOT NULL | Tipo de dato: 'double', 'int', etc. |
| `sensor_id` | UUID | FOREIGN KEY → sensors.id, NOT NULL, INDEX | ID del sensor |
| `device_id` | UUID | FOREIGN KEY → devices.id, NOT NULL, INDEX | ID del dispositivo |

**Índices Compuestos:**
- `idx_time_data_sensor_timestamp` (sensor_id, timestamp)
- `idx_time_data_device_timestamp` (device_id, timestamp)

**Relaciones:**
- `sensor` (N:1) - Pertenece a un sensor
- `device` (N:1) - Pertenece a un dispositivo
- `reports` (N:M) - Muchos datos pueden estar en muchos reportes (tabla intermedia: `report_time_data`)

---

### 11. `reports` - Reportes

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `name` | VARCHAR(255) | NOT NULL | Nombre del reporte |
| `description` | TEXT | NULL | Descripción del reporte |
| `business_id` | UUID | FOREIGN KEY → businesses.id, NOT NULL, INDEX | ID de la empresa |
| `branch_id` | UUID | FOREIGN KEY → branches.id, NOT NULL, INDEX | ID de la sucursal |
| `machine_id` | UUID | FOREIGN KEY → machines.id, NOT NULL, INDEX | ID de la máquina |
| `device_id` | UUID | FOREIGN KEY → devices.id, NOT NULL, INDEX | ID del dispositivo |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de última actualización |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Fecha de eliminación (soft delete) |

**Relaciones:**
- `business` (N:1) - Pertenece a una empresa
- `branch` (N:1) - Pertenece a una sucursal
- `machine` (N:1) - Pertenece a una máquina
- `device` (N:1) - Pertenece a un dispositivo
- `time_data` (N:M) - Un reporte contiene muchos datos temporales (tabla intermedia: `report_time_data`)

---

### 12. `report_time_data` - Tabla Intermedia (Reportes ↔ Datos Temporales)

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `report_id` | UUID | FOREIGN KEY → reports.id, PRIMARY KEY | ID del reporte |
| `time_data_id` | UUID | FOREIGN KEY → time_data.id, PRIMARY KEY | ID del dato temporal |

**Relación:** Tabla de asociación muchos-a-muchos entre `reports` y `time_data`.

---

### 13. `login_audits` - Auditoría de Inicios de Sesión

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `user_id` | UUID | FOREIGN KEY → users.id, NULL | ID del usuario (si existe) |
| `email` | VARCHAR(255) | NOT NULL, INDEX | Email usado en el intento |
| `ip_address` | VARCHAR(45) | NULL | Dirección IP (compatible IPv6) |
| `user_agent` | VARCHAR(500) | NULL | User agent del navegador/cliente |
| `success` | BOOLEAN | NOT NULL, DEFAULT FALSE | Si el login fue exitoso |
| `failure_reason` | VARCHAR(255) | NULL | Razón del fallo (si aplica) |
| `attempted_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha y hora del intento |

**Relaciones:**
- `user` (N:1) - Usuario asociado (puede ser NULL si el usuario no existe)

---

### 14. `revoked_tokens` - Tokens Revocados

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Identificador único |
| `jti` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | JWT ID (identificador único del token) |
| `token` | VARCHAR(500) | NOT NULL | Token completo para verificación |
| `revoked_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Fecha de revocación |
| `expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Fecha de expiración del token |

**Índices:**
- `idx_revoked_token_jti` (jti)

**Propósito:** Blacklist de tokens JWT revocados para prevenir su uso después del logout.

---

## 🔗 Resumen de Relaciones

### Relaciones Uno a Muchos (1:N)

- `Business` → `Branch` (1 empresa tiene N sucursales)
- `Business` → `Machine` (1 empresa tiene N máquinas)
- `Business` → `User` (1 empresa tiene N usuarios)
- `Business` → `Report` (1 empresa tiene N reportes)
- `Branch` → `User` (1 sucursal tiene N usuarios)
- `Branch` → `Machine` (1 sucursal tiene N máquinas)
- `Branch` → `Report` (1 sucursal tiene N reportes)
- `Role` → `User` (1 rol tiene N usuarios)
- `Machine` → `Device` (1 máquina tiene N dispositivos)
- `Machine` → `Sensor` (1 máquina tiene N sensores)
- `Machine` → `Report` (1 máquina tiene N reportes)
- `DeviceType` → `Device` (1 tipo tiene N dispositivos)
- `Device` → `Sensor` (1 dispositivo tiene N sensores)
- `Device` → `TimeData` (1 dispositivo genera N datos)
- `Device` → `Report` (1 dispositivo tiene N reportes)
- `SensorType` → `Sensor` (1 tipo tiene N sensores)
- `Sensor` → `TimeData` (1 sensor genera N datos)
- `User` → `LoginAudit` (1 usuario tiene N intentos de login)
- `User` → `Branch` (1 usuario puede ser representante de N sucursales)

### Relaciones Muchos a Muchos (N:M)

- `Report` ↔ `TimeData` (N reportes contienen M datos temporales)
  - Tabla intermedia: `report_time_data`

---

## 📌 Notas Importantes

1. **Soft Delete**: Las tablas principales (`businesses`, `branches`, `users`, `machines`, `devices`, `reports`) implementan soft delete mediante el campo `deleted_at`.

2. **Índices**: Se han creado índices en campos frecuentemente consultados:
   - Foreign keys
   - Campos únicos (`code`, `email`)
   - Campos de búsqueda frecuente (`timestamp` en `time_data`)
   - Índices compuestos para consultas optimizadas

3. **Seguridad**:
   - Las contraseñas se almacenan como hash en `users.password`
   - Los tokens revocados se registran en `revoked_tokens` para prevenir reutilización
   - Se auditan todos los intentos de login en `login_audits`

4. **Estados de Dispositivos**: Los dispositivos pueden tener los siguientes estados:
   - `created`: Recién creado
   - `active`: Activo y funcionando
   - `disabled`: Deshabilitado
   - `error`: En estado de error

5. **Tipos de Datos**: Los sensores pueden generar datos de diferentes tipos (`double`, `int`, etc.) especificados en `sensor_types.type` y `time_data.type`.
