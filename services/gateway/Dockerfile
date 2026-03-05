FROM nova-base:latest

COPY gateway/ ./gateway/

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8081"]
