#!/bin/bash

echo "🚀 Configurando Phishing Suite para Podman (sin root)..."

# Verificar si podman está disponible
if ! command -v podman &> /dev/null; then
    echo "❌ Podman no está instalado. Por favor instala podman:"
    echo "   sudo dnf install -y podman"
    exit 1
fi

# Verificar podman-compose o docker-compose
if ! command -v podman-compose &> /dev/null; then
    echo "📦 podman-compose no encontrado. Instalando via pip..."
    pip3 install --user podman-compose
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala python3:"
    echo "   sudo dnf install -y python3 python3-pip"
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado."
fi

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip3 install --user ansible requests python-dotenv

# Crear carpetas necesarias
echo "📁 Creando carpetas necesarias..."
mkdir -p reports
mkdir -p data

# Habilitar servicios de Podman para el usuario
echo "🔧 Configurando servicios de Podman para usuario..."
systemctl --user enable podman.socket 2>/dev/null || echo "⚠️  No se pudo habilitar podman.socket (normal en algunos sistemas)"
systemctl --user start podman.socket 2>/dev/null || echo "⚠️  No se pudo iniciar podman.socket (normal en algunos sistemas)"

# Verificar que podman funciona sin root
echo "🔍 Verificando que podman funciona..."
if ! podman info >/dev/null 2>&1; then
    echo "⚠️  Configurando podman para usuario sin privilegios..."
    # Crear configuración básica de podman
    mkdir -p ~/.config/containers
    if [ ! -f ~/.config/containers/storage.conf ]; then
        echo '[storage]
driver = "overlay"
runroot = "/run/user/1000/containers"
graphroot = "/home/'$USER'/.local/share/containers/storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"' > ~/.config/containers/storage.conf
    fi
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