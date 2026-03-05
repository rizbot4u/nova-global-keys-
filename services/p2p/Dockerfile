FROM nova-base:latest

COPY p2p/ ./p2p/

CMD ["uvicorn", "p2p.main:app", "--host", "0.0.0.0", "--port", "8005"]
