FROM python:3

WORKDIR /usr/src/orchestration_containers

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
