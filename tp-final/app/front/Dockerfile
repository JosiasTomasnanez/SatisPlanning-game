# Un ÚNICO Dockerfile para todas las versiones del front: lo único que cambia
# entre versiones es la carpeta de origen y el número. Así la diferencia entre
# stable y canary es solo el contenido, no la forma de construir la imagen.
#
# Uso (desde tp-final/app/front):
#   docker build --build-arg APP_VERSION=1.1.0 -t terrasense-front:1.1.0 .
# SRC por defecto es "v<APP_VERSION>"; se puede pisar con --build-arg SRC=...

# Imagen "unprivileged": nginx corre como usuario 101 y escucha en 8080
# (un puerto > 1024 no necesita root).
FROM nginxinc/nginx-unprivileged:1.27-alpine

ARG APP_VERSION=1.0.0
ARG SRC=v${APP_VERSION}

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY ${SRC}/ /usr/share/nginx/html/

# Pasamos a root SOLO durante el build para poder modificar los archivos
# copiados (pertenecen a root); en ejecución vuelve a correr como 101.
USER root

# Las 3 marcas de versión:
#  1) <meta name="app-version">: la ve el navegador / k6 browser en el DOM.
#  2) /version.txt: archivo liviano para probes y para contar con curl.
#  3) header X-App-Version: en toda respuesta de nginx (HTML, assets, 404).
RUN sed -i "/<head>/a <meta name=\"app-version\" content=\"${APP_VERSION}\">" /usr/share/nginx/html/index.html \
 && echo "${APP_VERSION}" > /usr/share/nginx/html/version.txt \
 && sed -i "s/__APP_VERSION__/${APP_VERSION}/g" /etc/nginx/conf.d/default.conf \
 && chown -R 101:101 /usr/share/nginx/html

USER 101
EXPOSE 8080
