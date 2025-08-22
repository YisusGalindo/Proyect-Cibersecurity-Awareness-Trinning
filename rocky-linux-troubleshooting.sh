#!/bin/bash

echo "🔧 Script de diagnóstico para Rocky Linux"
echo "========================================"

# Verificar sistema operativo
echo "📋 Sistema operativo:"
cat /etc/os-release | grep PRETTY_NAME

# Verificar Docker
echo ""
echo "🐳 Estado de Docker:"
if command -v docker &> /dev/null; then
    echo "✅ Docker instalado: $(docker --version)"
    if systemctl is-active --quiet docker; then
        echo "✅ Docker está corriendo"
    else
        echo "❌ Docker no está corriendo"
        echo "   Ejecuta: sudo systemctl start docker"
    fi
else
    echo "❌ Docker no está instalado"
    echo "   Ejecuta el paso 2 de la guía de instalación"
fi

# Verificar Docker Compose
echo ""
echo "🐳 Docker Compose:"
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose disponible: $(docker compose version --short)"
else
    echo "❌ Docker Compose no disponible"
fi

# Verificar Python
echo ""
echo "🐍 Python:"
if command -v python3 &> /dev/null; then
    echo "✅ Python3 instalado: $(python3 --version)"
else
    echo "❌ Python3 no está instalado"
    echo "   Ejecuta: sudo dnf install -y python3 python3-pip"
fi

# Verificar Ansible
echo ""
echo "⚙️ Ansible:"
if command -v ansible &> /dev/null; then
    echo "✅ Ansible instalado: $(ansible --version | head -n1)"
else
    echo "❌ Ansible no está instalado"
    echo "   Ejecuta: pip3 install --user ansible"
fi

# Verificar puertos
echo ""
echo "🌐 Puertos:"
if ss -tulpn | grep -q :8080; then
    echo "⚠️  Puerto 8080 está ocupado:"
    ss -tulpn | grep :8080
else
    echo "✅ Puerto 8080 disponible"
fi

if ss -tulpn | grep -q :3333; then
    echo "⚠️  Puerto 3333 está ocupado:"
    ss -tulpn | grep :3333
else
    echo "✅ Puerto 3333 disponible"
fi

# Verificar firewall
echo ""
echo "🔥 Firewall:"
if systemctl is-active --quiet firewalld; then
    echo "⚠️  Firewalld está activo"
    echo "   Puertos abiertos:"
    sudo firewall-cmd --list-ports 2>/dev/null || echo "   No se pudieron listar los puertos"
else
    echo "✅ Firewalld no está activo"
fi

# Verificar SELinux
echo ""
echo "🛡️  SELinux:"
if command -v sestatus &> /dev/null; then
    sestatus | grep "Current mode"
else
    echo "SELinux no disponible"
fi

# Verificar espacio en disco
echo ""
echo "💾 Espacio en disco:"
df -h / | tail -n1

# Verificar memoria
echo ""
echo "🧠 Memoria:"
free -h | grep Mem

# Verificar contenedores si Docker está corriendo
echo ""
echo "📦 Contenedores:"
if systemctl is-active --quiet docker; then
    if [ -f docker-compose.yml ]; then
        docker compose ps 2>/dev/null || echo "No hay contenedores corriendo"
    else
        echo "❌ No se encontró docker-compose.yml"
    fi
else
    echo "Docker no está corriendo"
fi

echo ""
echo "🔍 Diagnóstico completado"
echo ""
echo "💡 Sugerencias:"
echo "   - Si hay problemas con puertos, usa: sudo lsof -i :8080"
echo "   - Para ver logs: docker compose logs -f"
echo "   - Para reiniciar: docker compose restart"
echo "   - Para limpiar: docker compose down && docker compose up -d"