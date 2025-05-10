FROM node:18-bullseye-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para SHARP
RUN apt-get update && apt-get install -y \
  build-essential \
  libcairo2-dev \
  libjpeg-dev \
  libpango1.0-dev \
  libgif-dev \
  librsvg2-dev \
  libvips-dev \
  chromium \
  libnss3 \
  libfreetype6 \
  libharfbuzz0b \
  fonts-freefont-ttf \
  ca-certificates \
  curl \
  gnupg \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Prevenir descarga de binarios precompilados de sharp
ENV npm_config_sharp_binary_host=
ENV npm_config_sharp_libvips_binary_host=
ENV npm_config_sharp_prebuild=false
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Instalar dependencias
RUN npm install --force

EXPOSE 3008
CMD ["node", "app.js"]
