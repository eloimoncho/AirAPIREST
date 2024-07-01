FROM ubuntu:20.04

RUN apt-get update

RUN apt-get install -y sudo
RUN apt-get install -y nano
RUN apt-get install -y python3.7
RUN apt-get install -y python3-pip

RUN mkdir /app
WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt

EXPOSE 9000


