# pull official base image
FROM python:3.12.7-alpine

# set work directory
WORKDIR /usr/src/planilla

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary

# copy project
COPY . .

