#!/bin/bash

echo "🚀 Configurando Phishing Suite..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3 primero."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado. Puedes editarlo si necesitas cambiar configuraciones."
fi

# Instalar Ansible
echo "📦 Instalando dependencias de Python..."
pip3 install ansible requests python-dotenv

# Crear carpetas necesarias
echo "📁 Creando carpetas necesarias..."
mkdir -p reports
mkdir -p data

# Construir imágenes Docker
echo "🐳 Construyendo imágenes Docker..."
docker compose build

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
docker compose ps

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "🌐 Accede a la interfaz web en: http://localhost:8080"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: admin"
echo ""
echo "📊 GoPhish Admin en: http://localhost:3333"
echo ""
echo "📝 Para ver los logs: docker compose logs -f"
echo "🛑 Para detener: docker compose down"
echo ""
echo "⚠️  IMPORTANTE: Este sistema es solo para pruebas éticas de seguridad."
echo "   Asegúrate de tener autorización antes de usarlo."