FROM nova-base:latest

COPY user/ ./user/

CMD ["uvicorn", "user.main:app", "--host", "0.0.0.0", "--port", "8002"]
