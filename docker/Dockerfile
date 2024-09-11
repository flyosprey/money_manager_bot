FROM python:3.11-slim-buster

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME='/usr/local'

RUN apt-get update && \
    apt-get install -y curl libpq-dev gcc cron && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.in-project false && \
    poetry config installer.max-workers 10

WORKDIR /opt/money_manager_bot/

COPY money_manager /opt/money_manager_bot/money_manager
COPY tbot /opt/money_manager_bot/tbot
COPY tbot_base /opt/money_manager_bot/tbot_base
COPY manage.py /opt/money_manager_bot/manage.py
COPY poetry.lock /opt/money_manager_bot/poetry.lock
COPY pyproject.toml /opt/money_manager_bot/pyproject.toml
COPY start.sh /opt/money_manager_bot/start.sh
COPY cleanup_logs.sh /opt/money_manager_bot/cleanup_logs.sh

RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    poetry cache clear -n --no-ansi --all pypi

CMD ["/opt/money_manager_bot/start.sh"]
