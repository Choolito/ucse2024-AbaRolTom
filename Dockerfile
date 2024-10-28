# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de la aplicación
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Cambiamos el directorio de trabajo al directorio correcto antes de ejecutar el comando
WORKDIR /app/prode_project

# Crea el directorio para la base de datos
RUN mkdir -p /data

# Define el volumen para persistencia de datos
VOLUME ["/data"]

# Expone el puerto 8000
EXPOSE 8000

# Configura el comando de inicio del servidor y las migraciones
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000