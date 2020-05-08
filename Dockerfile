FROM tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11

RUN apk update && apk add libpq
RUN apk add --virtual .build-deps postgresql-dev gcc musl-dev

COPY requirements.txt /app/

WORKDIR /app
# Speed up the build of cassandra-driver since it can take quite long
ENV CASS_DRIVER_BUILD_CONCURRENCY=2
RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY . /app
ENV MODULE_NAME=app
ENV ENVIRONMENT=production
