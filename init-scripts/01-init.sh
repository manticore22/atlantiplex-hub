#!/bin/bash
# Database initialization script for PostgreSQL

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Create schema
    CREATE SCHEMA IF NOT EXISTS atlantiplex;

    -- Set default schema
    ALTER DATABASE $POSTGRES_DB SET search_path TO atlantiplex,public;
EOSQL

echo "Database initialization complete"
