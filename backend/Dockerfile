FROM python:3.10

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD sh -c "echo 'import json; data = json.load(open(\"/app/data/ingredients.json\")); fixture = [{\"model\": \"recipes.Ingredient\", \"fields\": item} for item in data]; json.dump(fixture, open(\"/app/data/ingredients_fixture.json\", \"w\"), ensure_ascii=False)' | python && \
           python manage.py makemigrations && \
           python manage.py migrate && \
           python manage.py collectstatic --noinput && \
           cp -r /app/collected_static/backend_static/. /backend_static/backend_static/ && \
           cp -r /app/media/. /backend_static/media/ && \
           if [ \"$USE_TEST_BASE\" = \"False\" ]; then \
               python manage.py loaddata /app/data/ingredients_fixture.json; \
               echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${ADMIN_USERNAME}', '${ADMIN_EMAIL}', '${ADMIN_PASSWORD}')\" | python manage.py shell; \
           fi && \
           gunicorn --bind 0.0.0.0:8000 backend.wsgi"