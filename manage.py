#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time

from django.conf import settings
from django.db.utils import OperationalError
from django.db import connections

from social_networking.settings import Settings


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
    main()
