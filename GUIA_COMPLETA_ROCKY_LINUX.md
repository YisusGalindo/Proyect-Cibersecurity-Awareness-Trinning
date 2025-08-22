# 🚀 Guía Completa - Phishing Suite en Rocky Linux (Desde Cero)

## 📋 Paso 1: Preparar el sistema

### Conectarse al servidor Rocky Linux
```bash
# Si es un servidor remoto
ssh usuario@ip-del-servidor

# Si es local, abrir terminal
```

### Actualizar el sistema
```bash
sudo dnf update -y
```

### Instalar herramientas básicas
```bash
sudo dnf install -y git curl wget vim nano htop
```

## 📋 Paso 2: Instalar Docker

### Agregar repositorio oficial de Docker
```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

### Instalar Docker y Docker Compose
```bash
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Configurar Docker
```bash
# Habilitar y iniciar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios de grupo
newgrp docker
```

### Verificar instalación de Docker
```bash
docker --version
docker compose version
```

**Salida esperada:**
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

## 📋 Paso 3: Instalar Python y dependencias

### Instalar Python 3 y pip
```bash
sudo dnf install -y python3 python3-pip python3-devel
```

### Instalar Ansible y dependencias
```bash
pip3 install --user ansible requests python-dotenv
```

### Agregar pip al PATH
```bash
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Verificar instalación
```bash
python3 --version
pip3 --version
ansible --version
```

## 📋 Paso 4: Clonar el repositorio del proyecto

### Crear directorio de trabajo
```bash
cd ~
mkdir -p proyectos
cd proyectos
```

### Clonar el repositorio (o crear estructura)
```bash
# Opción 1: Si tienes el repositorio en GitHub/GitLab
# git clone https://github.com/tu-usuario/phishing-suite.git
# cd phishing-suite

# Opción 2: Crear estructura manualmente
mkdir phishing-suite
cd phishing-suite
```

### Si creaste la estructura manualmente, necesitas crear todos los archivos
```bash
# Te ayudo a crear todos los archivos necesarios paso a paso
# Primero creamos la estructura de directorios

mkdir -p ansible/group_vars
mkdir -p ansible/inventory
mkdir -p ansible/playbooks
mkdir -p ansible/roles/docker_setup/tasks
mkdir -p ansible/roles/gophish_stack/tasks
mkdir -p ansible/roles/gophish_stack/files
mkdir -p ansible/roles/seed_gophish/tasks
mkdir -p ansible/roles/seed_gophish/files
mkdir -p ansible/roles/report_tools/tasks
mkdir -p flask_ui/templates
mkdir -p flask_ui/static
mkdir -p reporter
mkdir -p data
mkdir -p reports
```

## 📋 Paso 5: Crear archivos de configuración básicos

### Crear archivo .env
```bash
cat > .env << 'EOF'
# Credenciales de GoPhish (se generan automáticamente)
GOPHISH_API_KEY=
GOPHISH_ADMIN_USER=admin
GOPHISH_ADMIN_PASS=admin

# Credenciales de la interfaz web
UI_ADMIN_USER=admin
UI_ADMIN_PASS=admin

# URL de tracking (cambiar por tu dominio público)
TRACKING_URL=http://localhost

# Clave secreta de Flask (cambiar en producción)
FLASK_SECRET_KEY=change_me_in_production
EOF
```

### Crear docker-compose.yml
```bash
cat > docker-compose.yml << 'EOF'
services:
  gophish:
    image: gophish/gophish:latest
    container_name: gophish
    ports:
      - "3333:3333"
      - "80:80"
    networks:
      - phishing_net
    environment:
      GOPHISH_ADMIN_USER: ${GOPHISH_ADMIN_USER:-admin}
      GOPHISH_ADMIN_PASS: ${GOPHISH_ADMIN_PASS:-admin}
    volumes:
      - gophish_data:/opt/gophish
    restart: unless-stopped

  flask_ui:
    build: ./flask_ui
    container_name: phishing_ui
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      - ./ansible:/app/ansible:ro
      - ./reports:/app/reports
      - ./.last_campaign_id:/app/.last_campaign_id
      - ./build_groups.py:/app/build_groups.py:ro
    networks:
      - phishing_net
    depends_on:
      - gophish
    restart: unless-stopped

  reporter:
    build: ./reporter
    container_name: reporter
    env_file:
      - .env
    volumes:
      - ./reports:/out
    networks:
      - phishing_net
    restart: "no"

networks:
  phishing_net:
    driver: bridge

volumes:
  gophish_data:
EOF
```

### Crear script de instalación
```bash
cat > setup.sh << 'EOF'
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
pip3 install --user ansible requests python-dotenv

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
EOF

chmod +x setup.sh
```

## 📋 Paso 6: Configurar firewall (si está activo)

### Verificar estado del firewall
```bash
sudo systemctl status firewalld
```

### Si firewalld está activo, abrir puertos necesarios
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp  # Interfaz web
sudo firewall-cmd --permanent --add-port=3333/tcp  # GoPhish admin
sudo firewall-cmd --permanent --add-port=80/tcp    # Landing pages
sudo firewall-cmd --reload
```

### Verificar puertos abiertos
```bash
sudo firewall-cmd --list-ports
```

## 📋 Paso 7: Crear archivos mínimos necesarios

### Crear Flask UI básica
```bash
mkdir -p flask_ui

cat > flask_ui/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . /app

# Exponer puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
EOF

cat > flask_ui/requirements.txt << 'EOF'
Flask
Flask-Login
python-dotenv
requests
EOF

cat > flask_ui/app.py << 'EOF'
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phishing Suite</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #333; text-align: center; }
            .status { background: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎣 Phishing Suite - Infinity Air Springs</h1>
            <div class="status">
                <h3>✅ Sistema Iniciado Correctamente</h3>
                <p><strong>Interfaz Web:</strong> http://localhost:8080</p>
                <p><strong>GoPhish Admin:</strong> http://localhost:3333</p>
                <p><strong>Estado:</strong> Servicios en línea</p>
            </div>
            <p><strong>Próximos pasos:</strong></p>
            <ul>
                <li>Accede a GoPhish Admin para configurar campañas</li>
                <li>Revisa los logs con: <code>docker compose logs -f</code></li>
                <li>Para detener: <code>docker compose down</code></li>
            </ul>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
EOF
```

### Crear Reporter básico
```bash
mkdir -p reporter

cat > reporter/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "report.py"]
EOF

cat > reporter/requirements.txt << 'EOF'
requests
EOF

cat > reporter/report.py << 'EOF'
import os
import time

print("📊 Reporter iniciado...")
print("✅ Sistema listo para generar reportes")
time.sleep(5)
print("🏁 Reporter completado")
EOF
```

## 📋 Paso 8: Ejecutar el proyecto

### Construir e iniciar
```bash
# Dar permisos de ejecución
chmod +x setup.sh

# Ejecutar instalación
./setup.sh
```

### Verificar que todo funciona
```bash
# Ver estado de contenedores
docker compose ps

# Ver logs
docker compose logs -f
```

## 📋 Paso 9: Acceder a las interfaces

### Verificar conectividad
```bash
# Probar interfaz web
curl -I http://localhost:8080

# Probar GoPhish
curl -I http://localhost:3333
```

### Acceso desde navegador
- **Interfaz Web**: http://localhost:8080
- **GoPhish Admin**: http://localhost:3333

## 🔧 Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Reiniciar servicios
docker compose restart

# Detener todo
docker compose down

# Ver estado del sistema
docker compose ps
htop
df -h
```

## ❌ Solución de problemas

### Si Docker no funciona
```bash
sudo systemctl status docker
sudo systemctl start docker
```

### Si los puertos están ocupados
```bash
sudo lsof -i :8080
sudo lsof -i :3333
```

### Si hay problemas de permisos
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## ✅ Verificación final

Si todo funciona correctamente verás:

```bash
$ docker compose ps
NAME          STATUS
gophish       Up
phishing_ui   Up
reporter      Exited (0)
```

¡Listo! Tu Phishing Suite está funcionando en Rocky Linux.