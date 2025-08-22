# 🚀 Guía de Instalación - Phishing Suite en Rocky Linux

## 📋 Paso 1: Preparar el sistema

### Actualizar el sistema
```bash
sudo dnf update -y
```

### Instalar herramientas básicas
```bash
sudo dnf install -y git curl wget vim nano
```

## 📋 Paso 2: Instalar Docker

### Instalar Docker Engine
```bash
# Agregar repositorio oficial de Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Instalar Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Habilitar y iniciar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios de grupo (necesitas cerrar sesión y volver a entrar)
newgrp docker
```

### Verificar instalación de Docker
```bash
docker --version
docker compose version
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

### Agregar pip al PATH (si es necesario)
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

## 📋 Paso 4: Clonar y configurar el proyecto

### Clonar el repositorio (o crear la estructura)
```bash
# Si tienes el código en un repositorio
# git clone <tu-repositorio>
# cd phishing-suite

# O crear la estructura manualmente si ya tienes los archivos
mkdir -p phishing-suite
cd phishing-suite
```

### Crear archivo de configuración
```bash
cp .env.example .env
```

### Editar configuración (opcional)
```bash
nano .env
```

## 📋 Paso 5: Configurar firewall (si está activo)

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

## 📋 Paso 6: Construir e iniciar el proyecto

### Dar permisos de ejecución al script
```bash
chmod +x setup.sh
```

### Ejecutar el script de instalación
```bash
./setup.sh
```

### O ejecutar manualmente paso a paso:
```bash
# Crear carpetas necesarias
mkdir -p reports data

# Construir imágenes Docker
docker compose build

# Iniciar servicios
docker compose up -d
```

## 📋 Paso 7: Verificar que todo funciona

### Ver estado de los contenedores
```bash
docker compose ps
```

### Ver logs para verificar que no hay errores
```bash
docker compose logs -f
```

### Verificar conectividad
```bash
# Probar interfaz web
curl -I http://localhost:8080

# Probar GoPhish
curl -I http://localhost:3333
```

## 📋 Paso 8: Acceder a las interfaces

### Interfaz Web Principal
- **URL**: http://localhost:8080
- **Usuario**: admin
- **Contraseña**: admin

### GoPhish Admin
- **URL**: http://localhost:3333
- **Credenciales**: Se generan automáticamente (ver logs)

```bash
# Para ver las credenciales de GoPhish
docker compose logs gophish | grep -E "(admin|password|API)"
```

## 🔧 Comandos útiles para Rocky Linux

### Gestión de servicios
```bash
# Ver logs en tiempo real
docker compose logs -f

# Reiniciar servicios
docker compose restart

# Detener todo
docker compose down

# Limpiar todo (incluyendo volúmenes)
docker compose down -v
```

### Verificar puertos ocupados
```bash
ss -tulpn | grep :8080
ss -tulpn | grep :3333
```

### Verificar recursos del sistema
```bash
# Ver uso de memoria y CPU
htop

# Ver espacio en disco
df -h

# Ver procesos de Docker
docker stats
```

## ❌ Solución de problemas comunes en Rocky Linux

### Problema: SELinux bloquea Docker
```bash
# Verificar estado de SELinux
sestatus

# Si está en modo enforcing y causa problemas, puedes:
# Opción 1: Configurar SELinux para Docker (recomendado)
sudo setsebool -P container_manage_cgroup on

# Opción 2: Modo permisivo temporalmente (solo para pruebas)
sudo setenforce 0
```

### Problema: Firewall bloquea conexiones
```bash
# Verificar reglas activas
sudo firewall-cmd --list-all

# Deshabilitar firewall temporalmente (solo para pruebas)
sudo systemctl stop firewalld
```

### Problema: Permisos de Docker
```bash
# Si no puedes ejecutar docker sin sudo
sudo usermod -aG docker $USER
newgrp docker

# O reiniciar sesión
logout
# Volver a iniciar sesión
```

### Problema: Puertos ocupados
```bash
# Encontrar qué proceso usa el puerto
sudo lsof -i :8080
sudo lsof -i :3333

# Matar proceso si es necesario
sudo kill -9 <PID>
```

### Problema: Falta de espacio en disco
```bash
# Limpiar imágenes Docker no utilizadas
docker system prune -a

# Ver uso de espacio por Docker
docker system df
```

## 🔒 Configuración de seguridad adicional

### Configurar iptables (alternativa a firewalld)
```bash
# Si prefieres usar iptables
sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo dnf install -y iptables-services

# Configurar reglas básicas
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3333 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo service iptables save
```

### Configurar límites de recursos
```bash
# Editar docker-compose.yml para agregar límites
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '0.5'
```

## ✅ Verificación final

Si todo está funcionando correctamente, deberías ver:

```bash
$ docker compose ps
NAME          STATUS
gophish       Up
phishing_ui   Up
reporter      Exited (0)
```

Y poder acceder a:
- http://localhost:8080 ← Interfaz principal
- http://localhost:3333 ← GoPhish admin

## 📞 Soporte adicional

Si encuentras problemas específicos de Rocky Linux:

1. Revisa los logs: `docker compose logs -f`
2. Verifica la configuración de red: `ip addr show`
3. Comprueba el estado de los servicios: `systemctl status docker`
4. Revisa el espacio disponible: `df -h`

¡Listo! Tu Phishing Suite debería estar funcionando en Rocky Linux.