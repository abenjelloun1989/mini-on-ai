#!/usr/bin/env bash
# seed-ltd-codes.sh — bulk-insert LTD codes into the clauseguard D1 database
#
# Usage:
#   1. Open your PitchGround vendor dashboard → download your coupon codes CSV
#   2. Put one code per line in a file called codes.txt (just the code, no header)
#   3. Run: bash seed-ltd-codes.sh codes.txt
#
# The script builds a single SQL INSERT and runs it via wrangler d1 execute.
# Codes are stored uppercase. Existing codes are skipped (INSERT OR IGNORE).

set -e

CODES_FILE="${1:-codes.txt}"
DB_NAME="clauseguard"

if [[ ! -f "$CODES_FILE" ]]; then
  echo "Error: $CODES_FILE not found."
  echo "Usage: bash seed-ltd-codes.sh codes.txt"
  exit 1
fi

# Build VALUES list: ('CODE1'), ('CODE2'), ...
VALUES=$(while IFS= read -r line || [[ -n "$line" ]]; do
  code=$(echo "$line" | tr '[:lower:]' '[:upper:]' | tr -d '[:space:]')
  if [[ -n "$code" ]]; then
    echo "('${code}'),"
  fi
done < "$CODES_FILE" | sed '$ s/,$//')

if [[ -z "$VALUES" ]]; then
  echo "No codes found in $CODES_FILE"
  exit 1
fi

COUNT=$(echo "$VALUES" | wc -l | tr -d ' ')
echo "Seeding $COUNT codes into D1 ($DB_NAME)..."

SQL="INSERT OR IGNORE INTO ltd_codes (code) VALUES ${VALUES};"

npx wrangler d1 execute "$DB_NAME" --remote --command "$SQL"

echo "Done. $COUNT codes seeded."
