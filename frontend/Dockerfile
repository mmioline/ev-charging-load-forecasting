FROM docker.m.daocloud.io/library/python:3.12-slim

WORKDIR /app
COPY index.html .

CMD ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0"]
