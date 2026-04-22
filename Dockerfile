FROM python:3.11-slim

# Instalar dependencias del sistema para que SDL2 (el motor de Pygame) funcione
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del juego
COPY . .

# Comando de ejecución
CMD ["python", "main.py"]