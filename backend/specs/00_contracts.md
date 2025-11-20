# IoT Backend

Backend for centralization of data from multiple IoT devices.

## Stacks

### Frontend

- Typescript
- CSS Modules
- SASS

### Mobile
- iOS
  - Swift
  - SwiftUI
- Android
  - Kotlin
  - Jetpack Compose

### Backend
- Python
- FastAPI
- PostgreSQL

## Contracts

### Entities
1. TimeData
2. Sensor
3. SensorType
4. Device
5. DeviceType
6. Machine
7. User
8. Role
9. Report
10. Business
11. Branch

### Contracts
- TimeData
```json
{
  "id": "123",
  "timestamp": "2021-01-01T00:00:00Z",
  "value": 100,
  "unit": "°C",
  "type": "double",
  "sensor_id": "123",
  "device_id": "123",
}
```
- Sensor
```json
{
  "id": "123",
  "name": "temperature",
  "type_id": "123", // Relacional a SensorType
  "device_id": "123",
  "machine_id": "123",
}
```
- SensorType
```json
{
  "id": "123",
  "name": "Temperature",
  "code": "TEMP",
  "type": "double",
}
```
- Device
```json
{
  "id": "123",
  "name": "Device 1",
  "code": "DEV1",
  "description": "Device 1",
  "type_id": "123", // Relacional a DeviceType
  "machine_id": "123",
  "location": "123 Main St, Anytown, USA",
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
```
- DeviceType
```json
{
  "id": "123",
  "name": "Device Type 1",
  "code": "Smartphone",
}
```
- Machine
```json
{
  "id": "123",
  "name": "Machine 1",
  "code": "MACHINE1",
  "description": "Machine 1",
  "business_id": "123", // Relacional a Business
  "branch_id": "123", // Relacional a Branch
  "year": 2021,
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
```
- User
```json
{
  "id": "123",
  "first_name": "User 1",
  "last_name": "User 1",
  "profile_picture": "https://example.com/profile.jpg",
  "email": "user1@example.com",
  "password": "password",
  "role_id": "123", // Relacional a Role
  "business_id": "123", // Relacional a Business
  "branch_id": "123", // Relacional a Branch
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
```
- Role
```json
{
  "id": "123",
  "name": "Role 1",
  "description": "Role 1",
}
```
- Report
```json
{
  "id": "123",
  "name": "Report 1",
  "description": "Report 1",
  "business_id": "123", // Relacional a Business
  "branch_id": "123", // Relacional a Branch
  "machine_id": "123", // Relacional a Machine
  "device_id": "123", // Relacional a Device
  "time_data_ids": ["123", "124", "125"], // Relacional a TimeData
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
- Business
```json
{
  "id": "123",
  "name": "Business 1",
  "description": "Business 1",
  "picture_url": "https://example.com/business.jpg",
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
```
- Branch
```json
{
  "id": "123",
  "name": "Branch 1",
  "description": "Branch 1",
  "business_id": "123", // Relacional a Business
  "representative_id": "123", // Relacional a User
  "address": "123 Main St, Anytown, USA",
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
}
```


### Endpoints

#### IoT -> Gateway
- POST /v1/iot/data
```json
{
  "id": "123",
  "timestamp": "2021-01-01T00:00:00Z",
  "value": 100,
  "unit": "°C",
  "type": "double",
  "sensor_id": "123",
  "device_id": "123",
}
```

#### Gateway -> Frontend
##### Business
- GET /v1/dashboard/businesses -> List all businesses
- GET /v1/dashboard/businesses/{business_id} -> Read a business by id
```json
{
  "id": "123",
  "name": "Business 1",
  "description": "Business 1",
  "picture_url": "https://example.com/business.jpg",
  "created_at": "2021-01-01T00:00:00Z",
  "updated_at": "2021-01-01T00:00:00Z",
  "deleted_at": "2021-01-01T00:00:00Z",
  "branches": [
    {
      "id": "123",
      "name": "Branch 1",
      "description": "Branch 1",
      "business_id": "123",
      "representative_id": "123",
      "address": "123 Main St, Anytown, USA",
    }
  ]
}
```
- POST /v1/dashboard/businesses/ -> Create a business
- PUT /v1/dashboard/businesses/{business_id} -> Update a business by id
- DELETE /v1/dashboard/businesses/{business_id} -> Delete a business by id
##### Branches
- GET /v1/dashboard/branches/ -> List all branches
- GET /v1/dashboard/branches/business/{business_id} -> List all branches of a business
- GET /v1/dashboard/branches/{branch_id} -> Read a branch by id

- POST /v1/dashboard/branches/ -> Create a branch
- PUT /v1/dashboard/branches/{business_id}/{branch_id} -> Update a branch by id
- DELETE /v1/dashboard/branches/{business_id}/{branch_id} -> Delete a branch by id
##### Machines
- GET /v1/dashboard/machines/ -> List all machines
- GET /v1/dashboard/machines/branch/{branch_id} -> List all machines of a branch
- GET /v1/dashboard/machines/{machine_id} -> Read a machine by id
- POST /v1/dashboard/machines/ -> Create a machine
- PUT /v1/dashboard/machines/{machine_id} -> Update a machine by id
- DELETE /v1/dashboard/machines/{machine_id} -> Delete a machine by id
##### Devices
- GET /v1/dashboard/devices/ -> List all devices
- GET /v1/dashboard/devices/machine/{machine_id} -> List all devices of a machine
- GET /v1/dashboard/devices/{device_id} -> Read a device by id
- POST /v1/dashboard/devices/ -> Create a device
- PUT /v1/dashboard/devices/{device_id} -> Update a device by id
- DELETE /v1/dashboard/devices/{device_id} -> Delete a device by id
##### Sensors
- GET /v1/dashboard/sensors/ -> List all sensors
- GET /v1/dashboard/sensors/device/{device_id} -> List all sensors of a device
- GET /v1/dashboard/sensors/{sensor_id} -> Read a sensor by id
- POST /v1/dashboard/sensors/ -> Create a sensor
- PUT /v1/dashboard/sensors/{sensor_id} -> Update a sensor by id
- DELETE /v1/dashboard/sensors/{sensor_id} -> Delete a sensor by id
##### TimeData
- GET /v1/dashboard/time-data/ -> List all time data
- GET /v1/dashboard/time-data/sensor/{sensor_id} -> List all time data of a sensor
- GET /v1/dashboard/time-data/{time_data_id} -> Read a time data by id
- POST /v1/dashboard/time-data/ -> Create a time data
- PUT /v1/dashboard/time-data/{time_data_id} -> Update a time data by id
- DELETE /v1/dashboard/time-data/{time_data_id} -> Delete a time data by id
##### Reports
- GET /v1/dashboard/reports -> List all reports
- GET /v1/dashboard/reports/branch/{branch_id} -> List all reports of a branch
- GET /v1/dashboard/reports/machine/{machine_id} -> List all reports of a machine
- GET /v1/dashboard/reports/{report_id} -> Read a report by id
- POST /v1/dashboard/reports/ -> Create a report
- PUT /v1/dashboard/reports/{report_id} -> Update a report by id
- DELETE /v1/dashboard/reports/{report_id} -> Delete a report by id
##### Users
- GET /v1/dashboard/users -> List all users
- GET /v1/dashboard/users/{user_id} -> Read a user by id
- POST /v1/dashboard/users/ -> Create a user
- PUT /v1/dashboard/users/{user_id} -> Update a user by id
- DELETE /v1/dashboard/users/{user_id} -> Delete a user by id
