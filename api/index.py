import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Ensure DB is writable in serverless and run migrations on startup.
# Use tmp path on Vercel for SQLite.
os.environ.setdefault('DJANGO_DB_PATH', os.environ.get('DJANGO_DB_PATH', '/tmp/db.sqlite3'))

application = get_wsgi_application()

# Run migrations at start so tables exist.
from django.core.management import call_command
try:
    call_command('migrate', run_syncdb=True, verbosity=0)
except Exception:
    pass
