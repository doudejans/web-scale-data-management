FROM tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11

RUN apk update && apk add libpq
RUN apk add --virtual .build-deps postgresql-dev gcc musl-dev

COPY requirements.txt /app/

WORKDIR /app
RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY . /app
ENV MODULE_NAME=app

