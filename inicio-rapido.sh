#!/bin/bash

echo "🚀 Script de Inicio Rápido - Phishing Suite en Rocky Linux"
echo "=========================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar si es Rocky Linux
if ! grep -q "Rocky Linux" /etc/os-release 2>/dev/null; then
    print_warning "Este script está optimizado para Rocky Linux"
fi

# Paso 1: Actualizar sistema
echo ""
echo "📋 Paso 1: Actualizando el sistema..."
sudo dnf update -y
print_status "Sistema actualizado"

# Paso 2: Instalar herramientas básicas
echo ""
echo "📋 Paso 2: Instalando herramientas básicas..."
sudo dnf install -y git curl wget vim nano htop
print_status "Herramientas básicas instaladas"

# Paso 3: Instalar Docker
echo ""
echo "📋 Paso 3: Instalando Docker..."

if ! command -v docker &> /dev/null; then
    print_info "Agregando repositorio de Docker..."
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    print_info "Instalando Docker..."
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    print_info "Configurando Docker..."
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    
    print_status "Docker instalado y configurado"
else
    print_status "Docker ya está instalado"
fi

# Paso 4: Instalar Python y Ansible
echo ""
echo "📋 Paso 4: Instalando Python y Ansible..."

if ! command -v python3 &> /dev/null; then
    sudo dnf install -y python3 python3-pip python3-devel
    print_status "Python3 instalado"
else
    print_status "Python3 ya está instalado"
fi

if ! command -v ansible &> /dev/null; then
    pip3 install --user ansible requests python-dotenv
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
    export PATH=$PATH:~/.local/bin
    print_status "Ansible instalado"
else
    print_status "Ansible ya está instalado"
fi

# Paso 5: Crear directorio del proyecto
echo ""
echo "📋 Paso 5: Creando estructura del proyecto..."

cd ~
mkdir -p proyectos
cd proyectos

if [ ! -d "phishing-suite" ]; then
    mkdir phishing-suite
    print_status "Directorio del proyecto creado"
else
    print_status "Directorio del proyecto ya existe"
fi

cd phishing-suite

# Paso 6: Crear archivos básicos
echo ""
echo "📋 Paso 6: Creando archivos de configuración..."

# Crear .env
if [ ! -f .env ]; then
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
    print_status "Archivo .env creado"
fi

# Crear docker-compose.yml
if [ ! -f docker-compose.yml ]; then
    cat > docker-compose.yml << 'EOF'
services:
  gophish:
    image: gophish/gophish:latest
    container_name: gophish
    ports:
      - "3333:3333"
      - "80:80"
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
      - ./reports:/app/reports
    depends_on:
      - gophish
    restart: unless-stopped

volumes:
  gophish_data:
EOF
    print_status "Archivo docker-compose.yml creado"
fi

# Crear Flask UI
if [ ! -d flask_ui ]; then
    mkdir -p flask_ui
    
    cat > flask_ui/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8080
CMD ["python", "app.py"]
EOF

    cat > flask_ui/requirements.txt << 'EOF'
Flask
requests
EOF

    cat > flask_ui/app.py << 'EOF'
from flask import Flask, render_template_string
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Verificar estado de GoPhish
    gophish_status = "🔴 Desconectado"
    try:
        response = requests.get('http://gophish:3333', timeout=5)
        if response.status_code in [200, 302, 404]:
            gophish_status = "🟢 Conectado"
    except:
        pass
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phishing Suite</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 40px 20px; 
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
                margin: 10px 0;
            }
            .card { 
                background: rgba(255, 255, 255, 0.1); 
                backdrop-filter: blur(10px);
                padding: 30px; 
                border-radius: 15px; 
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .status-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .status-item h3 {
                margin: 0 0 10px 0;
                font-size: 1.5em;
            }
            .access-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .access-link {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            .access-link:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
                transform: translateY(-2px);
            }
            .commands {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                margin: 20px 0;
            }
            .commands h4 {
                margin-top: 0;
                color: #ffd700;
            }
            .command {
                background: rgba(0, 0, 0, 0.5);
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 3px solid #667eea;
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 2em; }
                .container { padding: 20px 10px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎣 Phishing Suite</h1>
                <p>Infinity Air Springs - Sistema de Pruebas de Seguridad</p>
            </div>
            
            <div class="card">
                <h2>📊 Estado del Sistema</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <h3>GoPhish</h3>
                        <p>{{ gophish_status }}</p>
                        <small>Puerto 3333</small>
                    </div>
                    <div class="status-item">
                        <h3>Interfaz Web</h3>
                        <p>🟢 Activa</p>
                        <small>Puerto 8080</small>
                    </div>
                    <div class="status-item">
                        <h3>Sistema</h3>
                        <p>🟢 Operativo</p>
                        <small>Rocky Linux</small>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🌐 Acceso a Interfaces</h2>
                <div class="access-links">
                    <a href="http://localhost:3333" target="_blank" class="access-link">
                        <h3>🎯 GoPhish Admin</h3>
                        <p>Panel de administración</p>
                        <small>localhost:3333</small>
                    </a>
                    <a href="http://localhost:8080" class="access-link">
                        <h3>🖥️ Interfaz Web</h3>
                        <p>Panel principal</p>
                        <small>localhost:8080</small>
                    </a>
                </div>
            </div>

            <div class="card">
                <h2>🔧 Comandos Útiles</h2>
                <div class="commands">
                    <h4>📋 Gestión de Contenedores:</h4>
                    <div class="command">docker compose ps</div>
                    <div class="command">docker compose logs -f</div>
                    <div class="command">docker compose restart</div>
                    <div class="command">docker compose down</div>
                    
                    <h4>🔍 Monitoreo:</h4>
                    <div class="command">htop</div>
                    <div class="command">df -h</div>
                    <div class="command">ss -tulpn | grep -E "(8080|3333)"</div>
                </div>
            </div>

            <div class="card">
                <h2>⚠️ Información Importante</h2>
                <ul>
                    <li><strong>Uso Ético:</strong> Este sistema es solo para pruebas autorizadas de seguridad</li>
                    <li><strong>Credenciales por defecto:</strong> admin/admin</li>
                    <li><strong>Configuración:</strong> Edita el archivo .env para personalizar</li>
                    <li><strong>Logs:</strong> Revisa los logs regularmente para monitorear el sistema</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    ''', gophish_status=gophish_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
EOF
    print_status "Flask UI creada"
fi

# Paso 7: Configurar firewall
echo ""
echo "📋 Paso 7: Configurando firewall..."

if systemctl is-active --quiet firewalld; then
    print_info "Configurando firewall..."
    sudo firewall-cmd --permanent --add-port=8080/tcp
    sudo firewall-cmd --permanent --add-port=3333/tcp
    sudo firewall-cmd --permanent --add-port=80/tcp
    sudo firewall-cmd --reload
    print_status "Puertos abiertos en firewall"
else
    print_status "Firewall no está activo"
fi

# Paso 8: Construir e iniciar
echo ""
echo "📋 Paso 8: Construyendo e iniciando servicios..."

print_info "Construyendo imágenes Docker..."
newgrp docker << EONG
docker compose build
EONG

print_info "Iniciando servicios..."
newgrp docker << EONG
docker compose up -d
EONG

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."
sleep 15

# Verificar estado
echo ""
echo "🔍 Verificando estado de los servicios..."
newgrp docker << EONG
docker compose ps
EONG

echo ""
echo "=========================================================="
print_status "¡Instalación completada!"
echo ""
echo "🌐 Accede a la interfaz web en: http://localhost:8080"
echo "📊 GoPhish Admin en: http://localhost:3333"
echo ""
echo "📝 Comandos útiles:"
echo "   - Ver logs: docker compose logs -f"
echo "   - Reiniciar: docker compose restart"
echo "   - Detener: docker compose down"
echo ""
print_warning "IMPORTANTE: Este sistema es solo para pruebas éticas de seguridad."
print_warning "Asegúrate de tener autorización antes de usarlo."
echo ""
echo "📍 Ubicación del proyecto: $(pwd)"
echo "=========================================================="