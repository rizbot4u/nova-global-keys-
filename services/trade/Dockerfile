FROM nova-base:latest

COPY trade/ ./trade/

CMD ["uvicorn", "trade.main:app", "--host", "0.0.0.0", "--port", "8004"]
