FROM tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11

# Add cassandra-driver dependencies
RUN apk update && apk add libpq
RUN apk add --virtual .build-deps postgresql-dev gcc musl-dev

# Speed up the build of cassandra-driver since it can take quite long (and allow for layer caching)
RUN CASS_DRIVER_BUILD_CONCURRENCY=2 pip install cassandra-driver==3.23.0

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY . /app

ENV MODULE_NAME=app
ENV ENVIRONMENT=production
