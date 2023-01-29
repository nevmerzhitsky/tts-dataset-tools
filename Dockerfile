FROM python:3.10

ENV PYTHONPYCACHEPREFIX=/tmp/python
ENV PYTHONUTF8=1

RUN set -e; \
    apt update; \
    apt install -y mc ffmpeg

RUN set -e; \
    python -m pip install --upgrade pip; \
    pip install pipenv

WORKDIR /var/app/src

COPY src/Pipfile* ./

RUN set -e; \
    pipenv install --deploy --system; \
    pipenv --clear

COPY src/ .

VOLUME /tmp
