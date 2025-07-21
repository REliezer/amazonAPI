# Amazon API 🛒

Una API REST moderna desarrollada con FastAPI para la gestión de productos estilo Amazon, incluyendo autenticación de usuarios, catálogo de productos y categorización.

## 🚀 Características

- **Autenticación completa**: Registro e inicio de sesión con Firebase
- **Gestión de productos**: Agregación de productos al catálogo y búsqueda de productos por categoría.
- **Categorización**: Sistema de categorías para organizar productos
- **Seguridad**: Validación de administradores y autenticación JWT
- **Monitoreo**: Telemetría integrada con Azure Application Insights
- **Cache**: Sistema de cache con Redis para optimizar rendimiento
- **Containerización**: Dockerizado para fácil despliegue

## 🛠️ Tecnologías Utilizadas

- **Framework**: FastAPI 0.116.1
- **Base de datos**: SQL Server (via pyodbc)
- **Autenticación**: Firebase Admin SDK
- **Cache**: Redis
- **Monitoreo**: Azure Application Insights
- **Containerización**: Docker
- **Cloud**: Azure (Container Registry, Key Vault)

## 📋 Requisitos Previos

- Python 3.13+
- Docker (opcional)
- SQL Server
- Firebase Project
- Azure Account (para producción)
- Redis (para cache)
- **Infraestructura Azure** (opcional): [Repositorio Terraform](https://github.com/REliezer/TerraformAmazonAPI) para crear automáticamente todos los recursos de Azure necesarios

## ⚡ Instalación Rápida

### Opción 1: Desarrollo Local

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/REliezer/amazonAPI
   cd amazonAPI
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**
   Si usas Key Vault solo debes crear un archivo `.env` con:
   ```env
   # Key Vault URL
   KEY_VAULT_URL=your_keyvault_url

   # Application Insights Configuration
   OTEL_SERVICE_NAME=your_otel_service_name
   OTEL_SERVER_VERSION=your_otel_server_version
   ```

4. **Ejecuta la aplicación**
   ```bash
   fastapi dev main.py
   ```

### Opción 2: Docker

1. **Construye la imagen**
   ```bash
   docker buildx build --platform linux/amd64 -t amazonapi:latest . --load
   ```

2. **Ejecuta el contenedor**
   ```bash
   docker run -d -p 8000:80 --name amazonapi-container --env-file .env amazonapi:latest
   ```

## 📡 Endpoints Principales

### Autenticación
- `POST /signup` - Registro de usuarios
- `POST /login` - Inicio de sesión

### Productos
- `GET /products` - Obtener todos los productos
- `POST /products` - Crear nuevo producto (requiere admin)
- `GET /products/?category_id={id}` - Productos por categoría

### Categorías
- `GET /category/name/?category_id={id}` - Nombre de categoría
- `GET /category/count` - Conteo de productos por categoría

### Sistema
- `GET /health` - Estado de la API
- `GET /` - Endpoint raíz

## 📊 Estructura del Proyecto

```
amazonAPI/
│
├── controllers/          # Lógica de negocio
│   ├── firebase.py      # Autenticación Firebase
│   ├── productscatalog.py # Gestión de productos
│   └── categories.py    # Gestión de categorías
│
├── models/              # Modelos Pydantic
│   ├── productscatalog.py
│   ├── userregister.py
│   ├── userlogin.py
│   └── productscategory.py
│
├── utils/               # Utilidades
│   ├── database.py      # Conexión a BD
│   ├── security.py      # Validaciones de seguridad
│   ├── telemetry.py     # Monitoreo
│   ├── redis_cache.py   # Cache
│   └── keyvault.py      # Azure Key Vault
│
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── Dockerfile          # Configuración Docker
└── README.md           # Este archivo
```

## 🔧 Configuración

### Azure Key Vault Secrets

Si decides usar Azure Key Vault (recomendado para producción), necesitas configurar los siguientes secrets:

| Secret Name | Descripción | Ejemplo |
|-------------|-------------|---------|
| `sql-driver` | Controlador ODBC para SQL Server | `ODBC Driver 17 for SQL Server` |
| `sql-server` | Servidor de base de datos | `your-server.database.windows.net` |
| `sql-database` | Nombre de la base de datos | `amazon_products_db` |
| `sql-username` | Usuario de la base de datos | `dbadmin` |
| `sql-password` | Contraseña de la base de datos | `your-secure-password` |
| `redis-connection-string` | Cadena de conexión completa a Redis | `rediss://your-redis.redis.cache.windows.net:6380,password=your-key` |
| `firebase-api-key` | API Key de Firebase para autenticación | `AIzaSyC...` |
|`applicationinsights-connection-string`| Connection string para Application Insights |
|`jwt-secret-key`| Secret key para generar los token | `your-token` |

> 💡 **Nota**: Los secrets en Key Vault reemplazan las variables de entorno locales para mayor seguridad en producción.

### Firebase Setup

1. **Credenciales de Admin SDK**
   - Descarga el archivo de credenciales desde Firebase Console
   - Colócalo en `secrets/firebase-secret.json`
   - O configúralo como variable de entorno `FIREBASE_CREDENTIALS`

2. **API Key para autenticación**
   - Obtén la Web API Key desde Firebase Console
   - Configúrala como `FIREBASE_API_KEY` o como secret `firebase-api-key` en Key Vault

### Base de Datos

La API utiliza SQL Server con el esquema `amazon`. 
   ```bash
   CREATE SCHEMA amazon;
   ```

**Tablas principales:**
- `amazon.products` - Catálogo de productos con campos como ASIN, título, precio, rating, etc.
   ```sql
      CREATE TABLE amazon.products (
         asin VARCHAR(255) PRIMARY KEY,
         title VARCHAR(255),
         imgUrl VARCHAR(255),
         productURL VARCHAR(255),
         stars FLOAT,
         price FLOAT,
         category_id INT REFERENCES amazon.categories(id)
      );
   ```
- `amazon.categories` - Categorías de productos
   ```sql
      CREATE TABLE amazon.categories (
         id INT IDENTITY(1,1) PRIMARY KEY,
         category_name VARCHAR(255)
      );
   ```
- `amazon.users` - Información de usuarios (sincronizado con Firebase)
   ```sql
      CREATE TABLE amazon.users (
         id INT IDENTITY(1,1) PRIMARY KEY,
         email VARCHAR(255) UNIQUE NOT NULL,
         password VARCHAR(255) NOT NULL,
         firstName VARCHAR(255),
         lastName VARCHAR(255),    
         active bit DEFAULT 1,
         admin bit DEFAULT 0
      );
   ```

**Origen de los datos:**
- Los datos para la base de datos fueron obtenidos de un dataset público de productos de Amazon obtenidos de Kaggle.
- Se utilizaron pipelines de datos automatizados para cargar y procesar la información en las tablas correspondientes
- Los pipelines incluyen procesos de limpieza, validación y transformación de datos antes de la inserción

**Procedimientos almacenados:**
- `amazon.users_insert` - Para registrar nuevos usuarios

## 🏗️ Infraestructura como Código

### Terraform (Recomendado)

Para crear automáticamente toda la infraestructura de Azure necesaria:

1. **Clona el repositorio de Terraform**
   ```bash
   git clone https://github.com/REliezer/TerraformAmazonAPI
   cd TerraformAmazonAPI
   ```

2. **Configura las variables**
   ```bash
   echo. > local.tfvars
   # Edita local.tfvars con tus valores de subscription_id y otros
   ```

3. **Despliega la infraestructura**
   ```bash
   terraform init
   terraform plan -var-file="local.tfvars"
   terraform apply -var-file="local.tfvars"
   ```

Esto creará automáticamente el Resource Group con:
- Azure Container Registry
- Azure Key Vault con los secrets necesarios
- Azure SQL Database
- Azure Cache for Redis
- Application Insights
- Azure Container Instances (opcional)
- Azure App Service
- Data Factory (V2)
- Storage Account

## 🚢 Despliegue

### Azure Container Registry

```bash
# Login al registry
az acr login --name acramazonproductsdev

# Tag de la imagen
docker tag amazonapi:latest acramazonproductsdev.azurecr.io/amazonapi:latest
docker tag amazonapi:latest acramazonproductsdev.azurecr.io/amazonapi:0.0.3

# Push al registry
docker push acramazonproductsdev.azurecr.io/amazonapi:latest
docker push acramazonproductsdev.azurecr.io/amazonapi:0.0.3
```

## 🔒 Seguridad

- **Autenticación**: JWT tokens via Firebase
- **Autorización**: Decorator `@validateadmin` para endpoints administrativos
- **Validación**: Modelos Pydantic con validaciones estrictas
- **Secrets**: Gestión segura con Azure Key Vault

## 📈 Monitoreo

- **Telemetría**: Azure Application Insights
- **Logs**: Logging estructurado con Python logging
- **Health Check**: Endpoint `/health` para monitoreo de estado

## 🤝 Contribución

1. Fork el proyecto
2. Crea una feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Ejecutar en modo desarrollo
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# O tambien
fastapi dev main.py

# Ver logs del contenedor
docker logs amazonapi-container

# Acceder al contenedor
docker exec -it amazonapi-container bash
```

### Estructura de Respuestas

```json
//Todos los productos /products
{
  "asin": "B08N5WRWNW",
  "title": "Echo Dot (4th Gen)",
  "imgUrl": "https://example.com/image.jpg",
  "productURL": "https://amazon.com/product",
  "stars": 4.5,
  "price": 49.99,
  "category_id": 1
}

//Productos de una categoria /products/?category_id=12
{
   "asin": "0804846332",
   "title": "Indonesian Batik Gift Wrapping Papers - 12 Sheets: 18 x 24 inch (45 x 61 cm) Wrapping Paper",
   "imgUrl": "https://m.media-amazon.com/images/I/A1DyRUpgDUL._AC_UL320_.jpg",
   "productURL": "https://www.amazon.com/dp/0804846332",
   "stars": 4.5,
   "price": 11.99,
   "category_id": 12
}
```

---

**Desarrollado con ❤️ para el curso de Expertos UNAH**
