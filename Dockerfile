FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS test

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_TOOL_BIN_DIR=/usr/local/bin

RUN apt update && \
    apt install --no-install-recommends -y \
    build-essential \
    gettext \
    tzdata \
    git \
    locales-all \
    wait-for-it \
    wget && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /srv

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY src /srv
