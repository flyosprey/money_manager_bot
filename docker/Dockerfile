###################################################################################################
# Build package
###################################################################################################

FROM python:3.11-slim-buster

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt update && \
    apt install -y \
        curl libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin && \
    poetry config virtualenvs.in-project true && \
    poetry config installer.max-workers 10

ENV VIRTUAL_ENV=/opt/money_manager_bot/.venv \
    PATH="/opt/money_manager_bot/.venv/bin:$PATH"

WORKDIR /opt/money_manager_bot/
COPY . /opt/money_manager_bot/
RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    poetry cache clear -n --no-ansi --all pypi
