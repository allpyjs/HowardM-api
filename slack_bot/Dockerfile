FROM python:3.9-slim

ARG GIT_COMMIT

WORKDIR /slack_bot
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY ./poetry.lock .
COPY ./pyproject.toml .
RUN poetry install --no-dev --no-root

COPY . .

ARG PORT
ENV PORT=${PORT:-"5003"}
ENV GIT_COMMIT=${GIT_COMMIT}

CMD gunicorn slack_bot:app --log-level info
