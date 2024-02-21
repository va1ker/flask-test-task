FROM python:3.11.0
RUN apt update \ 
    && apt install -y \
    postgresql
RUN mkdir /app
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false
RUN poetry install
COPY . .
