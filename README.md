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

2. **Crear un ambiente virtual (opcional pero recomendado)**
   ```bash
   # Crear ambiente virtual
   python -m venv venv
   
   # Activar el ambiente virtual
   # En Windows:
   .\venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   Si usas Key Vault solo debes crear un archivo `.env` con:
   ```env
   # Key Vault URL
   KEY_VAULT_URL=your_keyvault_url

   # Application Insights Configuration
   OTEL_SERVICE_NAME=your_otel_service_name
   OTEL_SERVER_VERSION=your_otel_server_version
   ```

5. **Ejecuta la aplicación**
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
   - Tambien lo puedes configurar como variable de entorno `FIREBASE_CREDENTIALS` o como secret en Key Vault

2. **API Key para autenticación**
   - Obtén la Web API Key desde Firebase Console
   - Configúrala como `FIREBASE_API_KEY` o como secret `firebase-api-key` en Key Vault

### Base de Datos

La API utiliza **SQL Server** con el esquema `amazon` para organizar todas las tablas.

#### 📝 Setup de Base de Datos

1. **Crear el esquema principal**:
   ```sql
   CREATE SCHEMA amazon;
   ```

2. **Crear las tablas en orden** (respetando las dependencias de claves foráneas):

   **Tabla de categorías** (debe crearse primero):
   ```sql
   CREATE TABLE amazon.categories (
       id INT IDENTITY(1,1) PRIMARY KEY,
       category_name VARCHAR(255) NOT NULL
   );
   ```

   **Tabla de productos** (depende de categories):
   ```sql
   CREATE TABLE amazon.products (
       asin VARCHAR(255) PRIMARY KEY,
       title VARCHAR(500) NOT NULL,
       imgUrl VARCHAR(500),
       productURL VARCHAR(500),
       stars FLOAT CHECK (stars >= 0 AND stars <= 5),
       price FLOAT CHECK (price >= 0),
       category_id INT NOT NULL,
       FOREIGN KEY (category_id) REFERENCES amazon.categories(id)
   );
   ```

   **Tabla de usuarios** (sincronizada con Firebase):
   ```sql
   CREATE TABLE amazon.users (
       id INT IDENTITY(1,1) PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       firstName VARCHAR(255) NOT NULL,
       lastName VARCHAR(255) NOT NULL,
       active BIT DEFAULT 1,
       admin BIT DEFAULT 0,
   );
   ```

3. **Crear procedimientos almacenados**:
   ```sql
   CREATE PROCEDURE amazon.users_insert
       @email VARCHAR(255),
       @firstName VARCHAR(255),
       @lastName VARCHAR(255),
       @active BIT = 1,
       @admin BIT = 0
   AS
   BEGIN
       INSERT INTO amazon.users (email, firstName, lastName, active, admin)
       VALUES (@email, @firstName, @lastName, @active, @admin);
       
       SELECT SCOPE_IDENTITY() as user_id;
   END;
   ```

#### 📊 Origen de los Datos

- **Dataset**: Los datos provienen de un dataset público de productos de Amazon obtenidos de **Kaggle**
- **Procesamiento**: Se utilizaron **pipelines automatizados** con las siguientes etapas:
  - 🧠 **Limpieza**: Remoción de datos duplicados y valores nulos
  - ✅ **Validación**: Verificación de formatos de URL, precios y ratings
  - 🔄 **Transformación**: Normalización de categorías y formateo de campos
  - 📥 **Carga**: Inserción ordenada respetando dependencias

#### 📋 Estructura de Tablas

| Tabla | Registros Aprox. | Descripción |
|-------|------------------|-------------|
| `categories` | ~248 | Categorías de productos (Hardware, Kids' Electronics, Cat Supplies, entre otras.) |
| `products` | ~1M+ | Catálogo completo de productos Amazon |
| `users` | Variable | Usuarios registrados (sincronizado con Firebase) |

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
## 🧪 Pruebas con Postman

### Colección de Pruebas

Se incluye una colección completa de Postman para probar todos los endpoints de la API:

**📁 Archivo**: `EXPERTOS PROD.postman_collection.json`

### Importar la Colección

1. **Abre Postman**
2. **Importa la colección**:
   - Clic en "Import" 
   - Selecciona el archivo `EXPERTOS PROD.postman_collection.json`
   - Confirma la importación

3. **Configura las variables**:
   - Ve a la colección → pestaña "Variables"
   - Actualiza la variable `domain` con tu URL:
     - **Local**: `http://localhost:8000`
     - **Producción**: `https://tu-api-domain.com`

### Pruebas Incluidas

La colección incluye pruebas para:

#### 🔐 Autenticación
- **POST** `/signup` - Registro de nuevos usuarios
- **POST** `/login` - Inicio de sesión y obtención de JWT

#### 📦 Productos
- **GET** `/products` - Listar todos los productos
- **POST** `/products` - Crear producto (requiere token admin)
- **GET** `/products/?category_id={id}` - Productos por categoría

#### 📂 Categorías
- **GET** `/category/name/?category_id={id}` - Obtener nombre de categoría
- **GET** `/category/count` - Conteo de productos por categoría

#### 🏥 Sistema
- **GET** `/health` - Health check de la API
- **GET** `/` - Endpoint raíz

### Variables de Entorno

La colección utiliza las siguientes variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `domain` | URL base de la API | `http://localhost:8000` |
| `token` | JWT token (se obtiene automáticamente al hacer login) | `eyJ0eXAiOiJKV1Q...` |

### Flujo de Pruebas Recomendado

1. **🏥 Health Check**: Verifica que la API esté funcionando
2. **👤 Registro**: Crea un usuario nuevo
3. **🔑 Login**: Inicia sesión para obtener token JWT
4. **📂 Categorías**: Prueba los endpoints de categorías
5. **📦 Productos**: Prueba listado y filtrado de productos
6. **⚙️ Admin**: Prueba creación de productos (requiere usuario admin)

### Notas Importantes

- 👑 Para probar endpoints de admin, necesitas un usuario con `admin: true`
- 🌐 Cambiar la variable `domain` según el entorno (local/producción)

---
