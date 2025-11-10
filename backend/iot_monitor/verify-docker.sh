#!/bin/bash
# Script para verificar que el volumen se montó correctamente

echo "Verificando que el contenedor esté corriendo..."
docker-compose ps

echo ""
echo "Listando contenido de /app en el contenedor:"
docker-compose exec api ls -la /app

echo ""
echo "Verificando que los archivos del proyecto estén presentes:"
docker-compose exec api test -f /app/pyproject.toml && echo "✓ pyproject.toml encontrado" || echo "✗ pyproject.toml NO encontrado"
docker-compose exec api test -d /app/app && echo "✓ carpeta app/ encontrada" || echo "✗ carpeta app/ NO encontrada"
docker-compose exec api test -f /app/app/main.py && echo "✓ app/main.py encontrado" || echo "✗ app/main.py NO encontrado"

echo ""
echo "Directorio de trabajo actual:"
docker-compose exec api pwd

