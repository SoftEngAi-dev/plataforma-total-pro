FROM node:22-bookworm-slim AS webbuild
WORKDIR /app
COPY web/package*.json web/
RUN cd web && npm ci --no-audit --no-fund
COPY . .
RUN python3 scripts/ensure_content.py
RUN cd web && ASTRO_BASE=/ npm run build

FROM python:3.12-slim
WORKDIR /app
COPY --from=webbuild /app /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PT_HOST=0.0.0.0
ENV PT_PORT=8787
ENV PT_DATA_DIR=/data
VOLUME ["/data"]
EXPOSE 8787
CMD ["python","local_server.py","--host","0.0.0.0","--port","8787"]
