FROM python:3.9-buster

ENV PYTHONUNBUFFERED 1
ENV DEBUG True

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate

CMD gunicorn data_plumber.wsgi:application --bind 0.0.0.0:8000
