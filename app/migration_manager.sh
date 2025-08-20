#!/usr/bin/env bash

set -e  # exit on any error

SCRIPT_NAME=$(basename "$0")

help_message() {
    cat <<EOF
Usage: $SCRIPT_NAME <command>

Commands:
  generate   Generate a new migration (requires input for message)
  apply      Apply the latest migration
  revert     Revert the last applied migration
  all        Generate and apply a migration

Examples:
  $SCRIPT_NAME generate "add users table"
  $SCRIPT_NAME apply
  $SCRIPT_NAME all "initial tables"
EOF
}

generate_migration() {
    if [ -z "$1" ]; then
        echo "Error: Migration message required."
        echo
        help_message
        exit 1
    fi
    echo "Generating migration: $1"
    alembic revision --autogenerate -m "$1"
}

apply_migration() {
    echo "Applying latest migration..."
    alembic upgrade head
}

downgrade_migration() {
    echo "Reverting last migration..."
    alembic downgrade -1
}

all() {
    if [ -z "$1" ]; then
        echo "Error: Migration message required."
        echo
        help_message
        exit 1
    fi
    generate_migration "$1" && apply_migration
}

# Main runner
case "$1" in
    generate)
        shift
        generate_migration "$@"
        ;;
    apply)
        apply_migration
        ;;
    revert)
        downgrade_migration
        ;;
    all)
        shift
        all "$@"
        ;;
    *)
        echo "Invalid or missing command."
        echo
        help_message
        exit 1
        ;;
esac
