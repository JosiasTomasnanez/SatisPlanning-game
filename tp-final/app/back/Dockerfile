# Imagen alpine: más chica = menos superficie de ataque y build más rápido.
FROM node:20-alpine
WORKDIR /app
# Copiamos primero package.json para aprovechar la caché de capas de Docker:
# si solo cambia server.js, no se reinstalan las dependencias.
COPY package.json ./
RUN npm install --omit=dev
COPY server.js ./
# Usuario sin privilegios: si alguien compromete el proceso, no es root.
USER node
EXPOSE 3000
CMD ["node", "server.js"]
