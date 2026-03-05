FROM nova-base:latest

COPY market/ ./market/

CMD ["uvicorn", "market.main:app", "--host", "0.0.0.0", "--port", "8003"]
