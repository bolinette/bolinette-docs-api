FROM python:3.9-slim-buster
WORKDIR /bolinette-docs
RUN apt-get update && apt-get install -y --no-install-recommends gcc make build-essential libc-dev \
    libffi-dev libssl-dev libpq-dev python3-dev cargo
RUN pip install --upgrade pip
RUN pip install wheel
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY bolinette_docs bolinette_docs
COPY manifest.blnt.yaml manifest.blnt.yaml
COPY env env
COPY server.py server.py
EXPOSE 5000
CMD ["python", "server.py", "run", "server"]
