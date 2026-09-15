.DEFAULT_GOAL := help

UV ?= uv
COMPOSE ?= docker compose


.PHONY: help
help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: sync
sync: ## Synchronize Python dependencies
	$(UV) sync


.PHONY: lint
lint: ## Run Ruff linting
	$(UV) run ruff check .


.PHONY: test
test: ## Run the complete test suite
	$(UV) run pytest


.PHONY: check
check: lint test ## Run all required local quality checks


.PHONY: api-config
api-config: ## Validate and display the Compose configuration
	$(COMPOSE) config


.PHONY: api-build
api-build: ## Build the API container image
	$(COMPOSE) build api


.PHONY: api-up
api-up: ## Start the API using the existing image
	$(COMPOSE) up --detach api


.PHONY: api-rebuild
api-rebuild: ## Rebuild the image and recreate the API container
	$(COMPOSE) up --detach --build --force-recreate api


.PHONY: api-ps
api-ps: ## Show the API container status
	$(COMPOSE) ps api


.PHONY: api-logs
api-logs: ## Follow API container logs
	$(COMPOSE) logs --follow api


.PHONY: api-down
api-down: ## Stop and remove the local Compose stack
	$(COMPOSE) down


.PHONY: api-restart
api-restart: api-down api-up ## Rebuild and restart the API