FROM python:3.9.9-slim-buster

ENV PYTHONUNBUFFERED 1

EXPOSE 8080
WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . ./
ENV PYTHONPATH app
ENTRYPOINT ["python", "app/main.py"]