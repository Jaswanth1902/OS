FROM python:3.9-slim

WORKDIR /app

COPY src/ml_stress.py .

CMD ["python", "ml_stress.py"]
