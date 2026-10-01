# Imagem única: a API (core/api.py) serve também o app web (mobile/dist)
# e as figuras das questões. Ver docs/DEPLOY.md.

FROM node:22-slim AS web
WORKDIR /app/mobile
COPY mobile/package.json mobile/package-lock.json ./
RUN npm ci
COPY mobile/ ./
RUN npx expo export --platform web

FROM python:3.12-slim
WORKDIR /app
COPY core/requirements-api.txt core/requirements-api.txt
RUN pip install --no-cache-dir -r core/requirements-api.txt
COPY core/ core/
COPY --from=web /app/mobile/dist mobile/dist
# Bancos de cada pessoa ficam no volume persistente montado em /data.
ENV API_PASTA_BANCOS=/data/bancos
WORKDIR /app/core
CMD python preparar_servidor.py && uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
