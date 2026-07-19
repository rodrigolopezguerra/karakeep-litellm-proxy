FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:80/health || exit 1
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","80","--no-access-log"]
