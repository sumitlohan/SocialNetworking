# Makefile for Django project

# Build Docker Image
build:
	docker-compose build

# Start Docker containers in detached mode
up-detach:
	docker-compose up -d

# Start Docker containers
up:
	docker-compose up

# # Apply database migrations
migrate:
	docker-compose run web python manage.py migrate

shell:
	docker-compose run web python manage.py shell

down:
	docker-compose down
