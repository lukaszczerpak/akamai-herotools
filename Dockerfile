FROM python:3.7-slim-buster
ENV LANG=en_US.UTF8
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app
RUN pip3 install .
