FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir flwr==1.5.0 tensorflow-cpu==2.13.0 python-socketio requests websocket-client

CMD ["python", "server_f2f.py"]