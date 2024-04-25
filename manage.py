#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time

from django.conf import settings
from django.db.utils import OperationalError
from django.db import connections

from social_networking.settings import Settings


def wait_for_db_connection():
    # Maximum number of retries
    max_retries = 10
    for alias in connections:
        for attempt in range(max_retries):
            connection = connections[alias]
            try:
                # Attempt to establish a database connection
                connection.ensure_connection()
                print(f"Connected to database '{alias}'!", flush=True)
                return
            except OperationalError as e:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: "
                    f"Unable to connect to database '{alias}'. Retrying in 2 seconds...", flush=True
                )
                time.sleep(2)
    # If maximum retries reached without success
    raise OperationalError("Unable to establish a connection to the database.")



def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_networking.settings')
    # configure class based settings.
    settings.configure(Settings())
    # It is possible that our other services initialise prior to our database connection. So, wait until our database connection setUp.
    wait_for_db_connection()
    main()
