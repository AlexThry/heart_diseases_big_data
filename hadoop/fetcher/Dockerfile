FROM python:3.8-slim

WORKDIR /app

copy . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "fetch.py"]
