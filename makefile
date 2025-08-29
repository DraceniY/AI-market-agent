# Makefile for Multi-Agent E-commerce System
# Usage: make <target>

# Variables
IMAGE_NAME = ecommerce-multi-agent
CONTAINER_NAME = ecommerce-agent
NETWORK_NAME = ecommerce-agent-network
VERSION = latest

# Environment variables (can be overridden)
PRODUCT_QUERY ?= "Adidas Samba sneakers"
SESSION_ID ?= "make-session-$(shell date +%s)"
AWS_REGION ?= us-west-2

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Multi-Agent E-commerce System - Docker Management"
	@echo "================================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Build targets
.PHONY: build
build: ## Build the Docker image
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME):$(VERSION) .
	@echo "✅ Build complete!"

.PHONY: start
start: ## Start container
	docker-compose up -d

.PHONY: run-simple
run-simple: ## Run single container without docker-compose
	@echo "Running simple container..."
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/results:/app/results \
		-v $(PWD)/config.ini:/app/config.ini:ro \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME):$(VERSION) \
		python main.py "$(PRODUCT_QUERY)" --session-id "$(SESSION_ID)"

.PHONY: analyze-simple
analyze-simple: 
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Please specify QUERY=<product_name>"; \
		exit 1; \
	fi
	@echo "Analyzing in simple mode: $(QUERY)"
	docker-compose run --rm ecommerce-agent python main.py "$(QUERY)" --simple --no-browser

.PHONY: analyze-dashboard
analyze-dashboard: ## Run analysis and copy dashboard to host
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Please specify QUERY=<product_name>"; \
		exit 1; \
	fi
	@echo "Analyzing with dashboard: $(QUERY)"
	docker-compose run --rm ecommerce-agent python main.py "$(QUERY)" --session-id "dashboard-$(shell date +%s)" --no-browser
	@echo "✅ Dashboard available in ./results/ "

.PHONY: generate-dashboard
generate-dashboard: ## Generate dashboard from existing JSON file
	@if [ -z "$(JSON_FILE)" ]; then \
		echo "❌ Please specify JSON_FILE=<path_to_json>"; \
		echo "Example: make generate-dashboard JSON_FILE=results/analysis_result_Adidas_Stan_Smith_20250829_090526.json"; \
		exit 1; \
	fi
	@echo "Generating dashboard from: $(JSON_FILE)"
	docker-compose run --rm -v $(PWD)/$(JSON_FILE):/app/input.json ecommerce-agent python main.py --dashboard-only /app/input.json --no-browser

# Management targets
.PHONY: logs
logs: ## Show application logs
	docker-compose logs -f ecommerce-agent

.PHONY: logs-all
logs-all: ## Show all service logs
	docker-compose logs -f

.PHONY: status
status: ## Show service status
	docker-compose ps

.PHONY: shell
shell: ## Access container shell
	docker-compose exec ecommerce-agent /bin/bash

.PHONY: shell-run
shell-run: ## Run new container with shell access
	docker-compose run --rm ecommerce-agent /bin/bash

# Cleanup targets
.PHONY: stop
stop: ## Stop all services
	@echo "Stopping services..."
	docker-compose down

.PHONY: clean
clean: ## Clean up containers and images
	@echo "Cleaning up..."
	docker-compose down --remove-orphans
	docker rmi $(IMAGE_NAME):$(VERSION) 2>/dev/null || echo "Image not found"
	docker system prune -f

.PHONY: clean-volumes
clean-volumes: ## Clean up containers, images, and volumes
	@echo "Cleaning up everything..."
	docker-compose down -v --remove-orphans
	docker rmi $(IMAGE_NAME):$(VERSION) 2>/dev/null || echo "Image not found"
	docker system prune -f -a

.PHONY: clean-data
clean-data: ## Clean generated data files
	@echo "Cleaning data files..."
	rm -rf data/* results/* sessions/*
	@echo "Data files cleaned!"

.PHONY: health
health: ## Check application health
	@echo "Checking application health..."
	docker-compose exec ecommerce-agent python -c "print('Application healthy!')"

