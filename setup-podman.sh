#!/bin/bash

echo "🚀 Configurando Phishing Suite para Podman..."

# Verificar Podman
if ! command -v podman &> /dev/null; then
    echo "❌ Podman no está instalado. Instalando..."
    dnf install -y podman podman-compose
fi

# Verificar podman-compose
if ! command -v podman-compose &> /dev/null; then
    echo "📦 Instalando podman-compose..."
    dnf install -y podman-compose
    # Si no está disponible en repos, instalar via pip
    if ! command -v podman-compose &> /dev/null; then
        pip3 install podman-compose
    fi
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Instalando..."
    dnf install -y python3 python3-pip
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado."
fi

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip3 install ansible requests python-dotenv

# Crear carpetas necesarias
echo "📁 Creando carpetas necesarias..."
mkdir -p reports
mkdir -p data

# Habilitar servicios de Podman
echo "🔧 Configurando servicios de Podman..."
systemctl --user enable podman.socket
systemctl --user start podman.socket

# Crear alias para docker si no existe
if ! grep -q "alias docker=podman" ~/.bashrc; then
    echo "alias docker=podman" >> ~/.bashrc
    echo "alias docker-compose=podman-compose" >> ~/.bashrc
    source ~/.bashrc
fi

# Construir imágenes con Podman
echo "🐳 Construyendo imágenes con Podman..."
podman-compose build

# Iniciar servicios
echo "🚀 Iniciando servicios..."
podman-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
podman-compose ps

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "🌐 Accede a la interfaz web en: http://localhost:8080"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: admin"
echo ""
echo "📊 GoPhish Admin en: http://localhost:3333"
echo ""
echo "📝 Para ver los logs: podman-compose logs -f"
echo "🛑 Para detener: podman-compose down"
echo ""
echo "⚠️  IMPORTANTE: Este sistema es solo para pruebas éticas de seguridad."
echo "   Asegúrate de tener autorización antes de usarlo."