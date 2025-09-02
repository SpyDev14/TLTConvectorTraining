FROM python:3.13.7-slim

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

EXPOSE 5000

RUN pip install pipenv && \
	pipenv install --system --deploy

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
