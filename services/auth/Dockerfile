FROM nova-base:latest

COPY auth/ ./auth/

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8001"]
