#!/usr/bin/env bash

set -e

echo "🚀 Generating SQLite database..."
python3 apps/SQLite_db/generate_db.py
echo "✅ Database generated!"
