FROM ghcr.io/berriai/litellm:main-stable

WORKDIR /app

COPY config.yaml .
COPY callbacks.py .

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:4000/health/liveliness || exit 1

ENTRYPOINT ["litellm"]
CMD ["--config", "/app/config.yaml", "--host", "0.0.0.0", "--port", "4000"]