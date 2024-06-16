FROM python:3.11-slim-buster

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && \
    apt-get install -y curl libpq-dev gcc firefox-esr && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin && \
    poetry config virtualenvs.in-project true && \
    poetry config installer.max-workers 10

ENV VIRTUAL_ENV=/opt/money_manager_bot/.venv \
    PATH="/opt/money_manager_bot/.venv/bin:$PATH"

WORKDIR /opt/money_manager_bot/

#COPY . /opt/money_manager_bot/

COPY .venv /opt/money_manager_bot/.venv
COPY money_manager /opt/money_manager_bot/money_manager
COPY tbot /opt/money_manager_bot/tbot
COPY tbot_base /opt/money_manager_bot/tbot_base
COPY .env.dev /opt/money_manager_bot/.env.dev
COPY manage.py /opt/money_manager_bot/manage.py
COPY poetry.lock /opt/money_manager_bot/poetry.lock
COPY poetry.toml /opt/money_manager_bot/poetry.toml
COPY pyproject.toml /opt/money_manager_bot/pyproject.toml
COPY start.sh /opt/money_manager_bot/start.sh

RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    poetry cache clear -n --no-ansi --all pypi

RUN curl -sSLo /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    rm /tmp/geckodriver.tar.gz

CMD ["/opt/money_manager_bot/start.sh"]
