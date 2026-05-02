#!/usr/bin/env bash
# =============================================================================
# generate-certs.sh — Генерация RSA-256 ключевой пары для JWT (auth)
# =============================================================================
# Использование:
#   bash infra/scripts/generate-certs.sh
# =============================================================================

set -euo pipefail

CERTS_DIR="services/auth/certs"

echo "🔑 Генерация RSA-2048 ключевой пары..."

mkdir -p "$CERTS_DIR"

# Приватный ключ
openssl genrsa -out "$CERTS_DIR/private_key.pem" 2048
echo "✅ Приватный ключ: $CERTS_DIR/private_key.pem"

# Публичный ключ (извлекается из приватного)
openssl rsa -in "$CERTS_DIR/private_key.pem" -pubout -out "$CERTS_DIR/public_key.pem"
echo "✅ Публичный ключ: $CERTS_DIR/public_key.pem"

# Безопасные права доступа
chmod 600 "$CERTS_DIR/private_key.pem"
chmod 644 "$CERTS_DIR/public_key.pem"

echo ""
echo "🎉 Готово! Ключи сохранены в $CERTS_DIR/"
echo "⚠️  Не добавляй private_key.pem в git! Убедись, что он в .gitignore"
