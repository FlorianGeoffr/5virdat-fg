FROM python:3.11.5-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apk add --no-cache --update nodejs npm
RUN npm i && npm run build && python manage.py collectstatic --no-input \
    && python manage.py makemigrations && python manage.py migrate
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
