#!/usr/bin/env bash
# =============================================================================
# migrate.sh — Применение Alembic-миграций для auth
# =============================================================================
# Использование:
#   bash infra/scripts/migrate.sh               # применить все миграции
#   bash infra/scripts/migrate.sh generate      # сгенерировать новую миграцию
#   bash infra/scripts/migrate.sh downgrade -1  # откатить на 1 версию назад
# =============================================================================

set -euo pipefail

SERVICE_DIR="services/auth"
ACTION="${1:-upgrade}"

# Берём параметры из .env (если есть)
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

DB_URL="postgresql+asyncpg://${AUTH_DB_USER:-auth_admin}:${AUTH_DB_PASSWORD:-auth_secret}@localhost:5432/${AUTH_DB_NAME:-lorelounge_auth}"

echo "📦 Alembic migration: $ACTION"
echo "🗄  DB: ${AUTH_DB_NAME:-lorelounge_auth} @ localhost:5432"
echo ""

cd "$SERVICE_DIR"

export CONFIG__DB__URL="$DB_URL"

case "$ACTION" in
  upgrade)
    echo "⬆️  Применяем миграции (upgrade head)..."
    ../../.venv/bin/alembic upgrade head
    echo "✅ Миграции применены"
    ;;
  generate)
    MSG="${2:-auto_migration}"
    echo "⚙️  Генерируем миграцию: '$MSG'..."
    ../../.venv/bin/alembic revision --autogenerate -m "$MSG"
    echo "✅ Файл миграции создан в alembic/versions/"
    ;;
  downgrade)
    STEP="${2:--1}"
    echo "⬇️  Откат: $STEP..."
    ../../.venv/bin/alembic downgrade "$STEP"
    echo "✅ Откат выполнен"
    ;;
  history)
    ../../.venv/bin/alembic history --verbose
    ;;
  current)
    ../../.venv/bin/alembic current
    ;;
  *)
    echo "❌ Неизвестная команда: $ACTION"
    echo "Доступные: upgrade | generate <msg> | downgrade <step> | history | current"
    exit 1
    ;;
esac
