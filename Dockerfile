FROM node:24-alpine3.23 AS frontend

WORKDIR /app

COPY opensmi-ui-frontend/package*.json .
RUN npm ci

COPY opensmi-ui-frontend/ .
RUN npm run build

FROM ghcr.io/astral-sh/uv:0.13.7-python3.12-alpine3.23

WORKDIR /app

# Install dependencies first (cached unless lockfile/pyproject changes)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Copy the application
COPY . /app
RUN uv sync --locked --no-dev

COPY --from=frontend /app/dist public/

# Use the virtualenv created by uv
ENV PATH="/app/.venv/bin:$PATH"

ARG INFO_IMAGE_TAG=undefined
ENV APP_VERSION=$INFO_IMAGE_TAG

CMD ["fastapi", "run", "--port", "8080"]
