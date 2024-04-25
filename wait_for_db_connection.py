import time
from django.db.utils import OperationalError
from django.db import connections


def wait_for_db_connection():
    # Maximum number of retries
    max_retries = 10
    for alias in connections:
        for attempt in range(max_retries):
            connection = connections[alias]
            try:
                # Attempt to establish a database connection
                connection.ensure_connection()
                print(f"Connected to database '{alias}'!")
                return
            except OperationalError as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Unable to connect to database '{alias}'. Retrying in 5 seconds...")
                print(f"Error: {e}")
                time.sleep(5)
    # If maximum retries reached without success
    raise OperationalError("Unable to establish a connection to the database.")


# Call the wait_for_db_connection function before accessing the database
# this is because sometimes, web service starts before the db service and we can get an error while
# accessing database in this case
wait_for_db_connection()
