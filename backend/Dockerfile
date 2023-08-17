FROM python:3.9-buster

ARG DEBUG
ENV DEBUG ${DEBUG}
RUN echo DEBUG${DEBUG}

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

CMD gunicorn data_plumber.wsgi:application --bind 0.0.0.0:8000
