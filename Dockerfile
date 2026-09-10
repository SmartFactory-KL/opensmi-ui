FROM node:24-alpine3.23 AS frontend

WORKDIR /app

COPY frontend/package*.json .
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM python:3.12-alpine3.23

WORKDIR /app

RUN apk add git

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

COPY --from=frontend /app/dist public/

ARG INFO_IMAGE_TAG=undefined
ENV APP_VERSION=$INFO_IMAGE_TAG

CMD ["fastapi", "run", "main.py", "--port", "8080"]
