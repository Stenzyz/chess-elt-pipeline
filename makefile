ifeq (,$(wildcard .env))
$(error .env not found. Run: cp .env.example .env — then fill in the values)
endif

include .env
export

SQL_DIR = ./sql
DBT_DIR = /opt/airflow/dbt/chess_dbt
DBT_RUN = docker compose exec -T airflow-scheduler dbt

.PHONY: all init build up down clean wait-db db-migrate test lint dbt-build dbt-refresh gen-keys

all: init

# Основной сценарий развёртывания

init: build up wait-db db-migrate
	@echo ""
	@echo "Setup complete."
	@echo "  Airflow:  http://localhost:8080"
	@echo "  Superset: http://localhost:8088"

build:
	@echo "Building custom images (airflow + superset)..."
	docker compose build

up:
	@echo "Starting containers..."
	docker compose up -d

wait-db:
	@echo "Waiting for postgres to become ready..."
	@until docker compose exec -T postgres pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} > /dev/null 2>&1; do \
		printf "."; \
		sleep 2; \
	done
	@echo " ready!"

down:
	docker compose down

clean:
	@echo "WARNING: this removes ALL volumes — raw data, Airflow and Superset metadata."
	@printf "Type 'yes' to continue: " && read ans && [ "$$ans" = "yes" ]
	docker compose down -v

# Генерация кодов

gen-keys:
	@echo "FERNET_KEY=$$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
	@echo "SUPERSET_SECRET_KEY=$$(openssl rand -base64 42)"
	@echo ""
	@echo "Copy these into your .env"

# Бд

db-migrate:
	@echo "Initilazing sql scripts from $(SQL_DIR) folder..."
	@if [ ! -d "$(SQL_DIR)" ]; then \
		echo "ERROR: no sql folder"; \
		exit 1; \
	fi
		@for file in $$(ls $(SQL_DIR)/*.sql | sort); do \
		echo "Now running $$file script..."; \
		docker compose exec -T postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
		-v pg_admin=${POSTGRES_USER} \
		-v ro_user=${SUPERSET_RO_USER} \
		-v ro_password=${SUPERSET_RO_PASSWORD} \
		< "$$file" || exit 1; \
	done
	@echo "All scripts from $(SQL_DIR) folder is OK!"

# Тесты

test:
	pytest

lint:
	ruff check .
	ruff format --check .

# dbt

dbt-build:
	$(DBT_RUN) build --project-dir $(DBT_DIR) --profiles-dir $(DBT_DIR)

dbt-refresh:
	$(DBT_RUN) build --full-refresh --project-dir $(DBT_DIR) --profiles-dir $(DBT_DIR)