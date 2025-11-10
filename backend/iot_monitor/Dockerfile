FROM python:3.11-slim

# Instalar uv para gestión de dependencias
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --frozen

# Copiar código de la aplicación
COPY app ./app
COPY specs ./specs

# Exponer puerto 8000
EXPOSE 8000

# Comando para ejecutar uvicorn con hot reload
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

