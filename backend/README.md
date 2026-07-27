# Backend

Django + GeoDjango (PostGIS) API for the map quiz game.

## Running the server

```bash
# from this directory, activate the venv
source ../venv/bin/activate

# make sure Postgres/PostGIS is running
sudo service postgresql start

# apply migrations (first run or after model changes)
python manage.py migrate

# start the dev server on port 8000
python manage.py runserver
``
