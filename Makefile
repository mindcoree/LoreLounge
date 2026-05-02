# =============================================================================
# Makefile — Удобные команды для разработки LoreLounge
# =============================================================================
# Использование:
#   make up          — поднять всё
#   make down        — остановить всё
#   make certs       — сгенерировать RSA-ключи для JWT
#   make migrate     — применить миграции auth
# =============================================================================

.PHONY: help up down build logs certs migrate migrate-gen ps clean

# Цвета
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

# Путь к compose-файлу (лежит в infra/)
COMPOSE := docker compose -f infra/docker-compose.yml

help: ## Показать список команд
	@echo ""
	@echo "$(GREEN)LoreLounge — доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ── Docker ────────────────────────────────────────────────────────────────────

up: ## Поднять все сервисы (сборка при необходимости)
	$(COMPOSE) up -d --build

down: ## Остановить все сервисы
	$(COMPOSE) down

build: ## Пересобрать образы
	$(COMPOSE) build --no-cache

logs: ## Логи всех сервисов (Ctrl+C для выхода)
	$(COMPOSE) logs -f

logs-auth: ## Логи только auth
	$(COMPOSE) logs -f auth

ps: ## Статус контейнеров
	$(COMPOSE) ps

clean: ## Остановить и удалить volumes (ОСТОРОЖНО: данные БД будут удалены!)
	$(COMPOSE) down -v

# ── Подготовка ────────────────────────────────────────────────────────────────

certs: ## Сгенерировать RSA-ключи для JWT (auth)
	@bash infra/scripts/generate-certs.sh

# ── Миграции ─────────────────────────────────────────────────────────────────

db-up: ## Запустить только БД auth (для локальных миграций)
	$(COMPOSE) up -d postgres_auth

migrate: ## Применить Alembic-миграции (auth)
	@bash infra/scripts/migrate.sh upgrade

migrate-gen: ## Сгенерировать новую миграцию: make migrate-gen MSG="add_novels_table"
	@bash infra/scripts/migrate.sh generate "$(MSG)"

migrate-history: ## История миграций
	@bash infra/scripts/migrate.sh history

migrate-current: ## Текущая версия миграций
	@bash infra/scripts/migrate.sh current
