FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR /jupyterLabFolder

RUN pip install jupyterlab

RUN apt-get update

RUN apt-get install sudo -y