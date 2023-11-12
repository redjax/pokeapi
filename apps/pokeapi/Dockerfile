FROM python:3.11-slim as base

## Environment
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    ## Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

FROM base AS build

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM build AS dev

ENV ENV_FOR_DYNACONF=dev

WORKDIR /app
COPY ./src /app

# EXPOSE 5000

# CMD ["python", "start_server.py"]

FROM build AS prod

ENV ENV_FOR_DYNACONF=prod

WORKDIR /app
COPY ./src/* .

# EXPOSE 5000

# CMD ["python", "start_server.py"]