# Use the official Python 3.8 image as a base image
FROM python:3.8

SHELL ["/bin/bash", "-c"]

# Set working directory in the container
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile ./Pipfile
COPY Pipfile.lock ./Pipfile.lock

# Install pipenv
RUN pip install pipenv

# Install dependencies using pipenv
RUN pipenv install --dev --system --deploy

# Copy the Django project files to the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

