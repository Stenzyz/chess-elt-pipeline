include .env
export

SQL_DIR = ./sql

all: db-up

db-up: db-migrate
	@echo "Database ${POSTGRES_DB} fully initialized!"

db-migrate:
	@echo "Initilazing sql scripts from $(SQL_DIR) folder..."
	@if [ ! -d "$(SQL_DIR)" ]; then \
		echo "ERROR: no sql folder"; \
		exit 1; \
	fi
		@for file in $$(ls $(SQL_DIR)/*.sql | sort); do \
		echo "Now running $$file script..."; \
		docker compose exec -T postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < "$$file" || exit 1; \
	done
	@echo "All scripts from $(SQL_DIR) folder is OK!"
