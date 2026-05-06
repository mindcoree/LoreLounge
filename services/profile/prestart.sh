#!/usr/bin/env bash

set -e

echo "Run apply migrations.."
alembic -c src/infrastructure/db/alembic.ini upgrade head
echo "Migrations applied"


exec "$@"

