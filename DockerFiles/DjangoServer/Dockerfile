FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN pip3 install Django

RUN pip3 install psycopg2-binary

RUN pip3 install django-cors-headers

RUN pip3 install requests

RUN pip3 install uwsgi

RUN apt-get update

RUN apt-get install nginx -y

RUN apt-get install sudo -y

RUN ln -s /code/nginx.conf /etc/nginx/sites-enabled/

RUN groupadd -g 1001 uwsgigroup

RUN useradd -u 1001 -g uwsgigroup uwsgi