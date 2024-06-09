FROM python:3.12-alpine AS build
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pip-tools
WORKDIR /usr/src/analog
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt


FROM build AS test
# Install docker and docker compose for use with pytest-docker
RUN apk add --update docker-cli docker-cli-compose
COPY requirements/requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY pyproject.toml .
RUN pip install -e .


FROM build as prod
COPY src src/
COPY pyproject.toml .
RUN pip install .
