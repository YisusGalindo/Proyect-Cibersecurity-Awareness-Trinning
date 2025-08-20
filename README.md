# Phishing Suite - Infinity Air Springs

## 🚀 Instalación Rápida

### Prerrequisitos
- Docker y Docker Compose instalados
- Python 3.8+ (para Ansible)
- Git

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd phishing-suite
```

### 2. Instalar dependencias
```bash
# Instalar Ansible
pip install ansible requests

# O si prefieres usar un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install ansible requests
```

### 3. Configurar variables de entorno
```bash
# Editar el archivo .env con tus configuraciones
cp .env.example .env
nano .env  # o tu editor preferido
```

### 4. Configurar SMTP (opcional pero recomendado)
```bash
# Editar configuración SMTP
nano data/smtp.env
```

### 5. Construir e iniciar los servicios
```bash
# Construir las imágenes Docker
docker compose build

# Iniciar todos los servicios
docker compose up -d
```

### 6. Verificar que todo esté funcionando
```bash
# Ver logs de los contenedores
docker compose logs -f

# Verificar que los servicios estén corriendo
docker compose ps
```

## 🎯 Uso

### Acceso a las interfaces
- **Interfaz Web Principal**: http://localhost:8080
  - Usuario: `admin`
  - Contraseña: `admin`
- **GoPhish Admin**: http://localhost:3333
  - Las credenciales se generan automáticamente

### Flujo de trabajo
1. Accede a http://localhost:8080
2. Inicia sesión con las credenciales por defecto
3. Haz clic en "🚀 Iniciar Campaña"
4. Monitorea los resultados en el Dashboard
5. Genera reportes PDF cuando termine la campaña

## ⚙️ Configuración

### Variables de entorno (.env)
```bash
# Credenciales de GoPhish (se generan automáticamente)
GOPHISH_API_KEY=
GOPHISH_ADMIN_USER=admin
GOPHISH_ADMIN_PASS=admin

# Credenciales de la interfaz web
UI_ADMIN_USER=admin
UI_ADMIN_PASS=admin

# URL de tracking (cambiar por tu dominio público)
TRACKING_URL=http://localhost

# Clave secreta de Flask
FLASK_SECRET_KEY=change_me_in_production
```

### Configuración SMTP (data/smtp.env)
```bash
SMTP_HOST=smtp.tuempresa.com
SMTP_PORT=587
SMTP_USER=phishing@tuempresa.com
SMTP_PASS=TuPasswordSMTP
SMTP_FROM_NAME=Soporte TI
SMTP_FROM_EMAIL=soporte@tuempresa.com
```

### Lista de empleados (data/employees.csv)
El archivo ya incluye datos de ejemplo. Puedes modificarlo con los empleados reales:
```csv
first_name,last_name,email,department,region
Fernando,Herrera,fernando.herrera@infinityairsprings.com,TI,MX
...
```

## 🔧 Comandos útiles

### Docker
```bash
# Ver logs en tiempo real
docker compose logs -f

# Reiniciar un servicio específico
docker compose restart flask_ui

# Detener todos los servicios
docker compose down

# Limpiar todo (incluyendo volúmenes)
docker compose down -v
```

### Ansible (manual)
```bash
# Desplegar desde cero
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy.yml

# Solo iniciar campaña
ansible-playbook -i ansible/inventory.ini ansible/playbooks/start_campaign.yml

# Generar reporte
ansible-playbook -i ansible/inventory.ini ansible/playbooks/report.yml
```

## 📊 Características

- ✅ Interfaz web intuitiva
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Generación automática de reportes PDF
- ✅ Plantillas de email personalizables
- ✅ Landing pages realistas
- ✅ Segmentación por departamento y región
- ✅ Historial completo de campañas
- ✅ Automatización completa con Ansible

## 🛡️ Seguridad

- Cambiar las credenciales por defecto en producción
- Usar HTTPS en entornos de producción
- Configurar firewall apropiado
- Mantener los contenedores actualizados

## 🐛 Solución de problemas

### Error: "Ansible no está instalado"
```bash
pip install ansible
```

### Error: "No se puede conectar a GoPhish"
```bash
# Verificar que el contenedor esté corriendo
docker compose ps
docker compose logs gophish
```

### Error: "No se pueden enviar emails"
- Verificar configuración SMTP en `data/smtp.env`
- Comprobar credenciales del servidor de email
- Revisar logs: `docker compose logs gophish`

### Los reportes no se generan
```bash
# Verificar que la carpeta reports existe
ls -la reports/

# Ver logs del reporter
docker compose logs reporter
```

## 📝 Notas importantes

- Este es un sistema para **pruebas éticas de seguridad** únicamente
- Obtener autorización antes de usar en cualquier organización
- Cumplir con todas las leyes y regulaciones locales
- Usar solo en redes y sistemas propios o autorizados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request