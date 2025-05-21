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

RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl libpq-dev gcc cron git \
    libnss3 libgconf-2-4 libxss1 libappindicator1 libindicator7 \
    fonts-liberation libasound2 libatk-bridge2.0-0 libcups2 libdrm2 libgtk-3-0 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

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

RUN mkdir -p /opt/money_manager_bot/logs && chmod -R 755 /opt/money_manager_bot/logs


RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    poetry cache clear -n --no-ansi --all pypi

EXPOSE 443
EXPOSE 80
EXPOSE 8000

CMD ["/opt/money_manager_bot/start.sh"]
