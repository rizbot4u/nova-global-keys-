FROM nova-base:latest

COPY broker/ ./broker/

CMD ["uvicorn", "broker.main:app", "--host", "0.0.0.0", "--port", "8006"]
