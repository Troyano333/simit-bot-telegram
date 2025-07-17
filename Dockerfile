    # Usa una imagen base de Python con Playwright preinstalado.
    # Esta imagen ya incluye los navegadores y las dependencias del sistema.
    FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

    # Establece el directorio de trabajo dentro del contenedor
    WORKDIR /app

    # Copia tu archivo de requisitos al contenedor
    COPY requirements.txt .

    # Instala las dependencias de Python
    RUN pip install --no-cache-dir -r requirements.txt

    # Copia el resto de tus archivos de aplicación al contenedor
    COPY . .

    # Comando para ejecutar el bot cuando el contenedor se inicie
    # Esto es equivalente a tu Procfile, pero dentro del Dockerfile
    CMD ["python", "bot.py"]
    
