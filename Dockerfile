FROM gcr.io/kaggle-images/python:latest

WORKDIR /app

ADD ./requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
