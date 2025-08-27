# Procesador de Tarifas Eléctricas

Aplicación web para procesar archivos PDF y CSV de tarifas eléctricas de diferentes comercializadores.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona este repositorio o descarga los archivos
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto
2. Agrega tu clave API de Anthropic:
   ```
   ANTHROPIC_API_KEY=tu_clave_api_aqui
   ```

## Uso

1. Inicia la aplicación:
   ```bash
   python app.py
   ```
2. Abre tu navegador y ve a `http://localhost:5000`
3. Selecciona el archivo PDF o CSV que deseas procesar
4. Elige el comercializador correspondiente
5. Haz clic en "Procesar Archivo"
6. El archivo CSV procesado se descargará automáticamente

## Estructura del Proyecto

```
.
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias del proyecto
├── .env                  # Variables de entorno (no incluido en el repo)
├── templates/            # Plantillas HTML
│   └── index.html       # Página principal
├── uploads/             # Directorio temporal para archivos subidos
└── src/                 # Código fuente
    └── tarifas_processor.py  # Procesador de tarifas
```

## Notas

- Los archivos subidos se procesan temporalmente y se eliminan después de la descarga
- El tamaño máximo de archivo permitido es de 16MB
- Se admiten archivos PDF y CSV 