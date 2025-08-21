# 🚀 Guía Paso a Paso - Phishing Suite

## 📋 Paso 1: Verificar el estado actual

```bash
# Ver qué está pasando con los contenedores
docker compose logs -f
```

**Presiona Ctrl+C para salir de los logs**

## 📋 Paso 2: Detener todo y limpiar

```bash
# Detener todos los servicios
docker compose down

# Limpiar contenedores y volúmenes (opcional, solo si hay problemas)
docker compose down -v
```

## 📋 Paso 3: Verificar archivos necesarios

```bash
# Verificar que existe el archivo .env
ls -la .env

# Si no existe, crearlo
cp .env.example .env
```

## 📋 Paso 4: Crear archivos faltantes

```bash
# Crear Dockerfile para Flask UI
mkdir -p flask_ui
```

## 📋 Paso 5: Construir las imágenes

```bash
# Construir todas las imágenes
docker compose build --no-cache
```

## 📋 Paso 6: Iniciar los servicios

```bash
# Iniciar todos los servicios
docker compose up -d
```

## 📋 Paso 7: Verificar que todo funciona

```bash
# Ver el estado de los contenedores
docker compose ps

# Ver logs si hay problemas
docker compose logs gophish
docker compose logs flask_ui
```

## 📋 Paso 8: Esperar a que GoPhish esté listo

```bash
# Esperar 30 segundos para que GoPhish genere la API key
sleep 30

# Ver los logs de GoPhish para obtener las credenciales
docker compose logs gophish | grep -E "(admin|password|API)"
```

## 📋 Paso 9: Acceder a las interfaces

1. **Interfaz Web Principal**: http://localhost:8080
   - Usuario: `admin`
   - Contraseña: `admin`

2. **GoPhish Admin**: http://localhost:3333
   - Las credenciales aparecen en los logs de GoPhish

## 📋 Paso 10: Probar el sistema

1. Accede a http://localhost:8080
2. Inicia sesión con admin/admin
3. Haz clic en "🚀 Iniciar Campaña"
4. Monitorea los resultados

## 🔧 Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Reiniciar un servicio específico
docker compose restart flask_ui

# Detener todo
docker compose down

# Ver qué puertos están ocupados
netstat -tulpn | grep :8080
netstat -tulpn | grep :3333
```

## ❌ Solución de problemas comunes

### Problema: Puerto ocupado
```bash
# Matar proceso en puerto 8080
sudo fuser -k 8080/tcp

# Matar proceso en puerto 3333
sudo fuser -k 3333/tcp
```

### Problema: Permisos
```bash
# Cambiar permisos de archivos
chmod +x setup.sh
chmod 644 .env
```

### Problema: Contenedores no inician
```bash
# Limpiar todo y empezar de nuevo
docker compose down -v
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

## ✅ Verificación final

Si todo funciona correctamente deberías ver:

```bash
docker compose ps
```

**Salida esperada:**
```
NAME          STATUS
gophish       Up
phishing_ui   Up
reporter      Exited (0)
```

**URLs de acceso:**
- http://localhost:8080 ← Interfaz principal
- http://localhost:3333 ← GoPhish admin