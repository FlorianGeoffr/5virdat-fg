#!/usr/bin/env bash
# exit on error
set -o errexit

# Install & Execute WebPack 
npm i
npm run build

python -m pip install --upgrade pip

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
