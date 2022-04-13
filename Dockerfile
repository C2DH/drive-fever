FROM python:3.6.9-alpine

WORKDIR /drive-fever

ARG GIT_TAG
ARG GIT_BRANCH
ARG GIT_REVISION

RUN pip install -U pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

COPY download.py .

ENV DRIVE_FEVER_GIT_TAG=${GIT_TAG}
ENV DRIVE_FEVER_GIT_BRANCH=${GIT_BRANCH}
ENV DRIVE_FEVER_GIT_REVISION=${GIT_REVISION}
