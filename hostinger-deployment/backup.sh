#!/bin/bash
# Backup Script for Hostinger Deployment
# Backs up database and volumes

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_USER=${DB_USER:-atlantiplex}

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)..."

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump -U "$DB_USER" atlantiplex | gzip > "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"
echo "✓ PostgreSQL backup complete"

# Backup Redis
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli BGSAVE
docker-compose exec -T redis cat /data/dump.rdb | gzip > "$BACKUP_DIR/redis_$TIMESTAMP.rdb.gz"
echo "✓ Redis backup complete"

# Backup volumes
echo "Backing up volumes..."
tar -czf "$BACKUP_DIR/volumes_$TIMESTAMP.tar.gz" -C /var/lib/docker/volumes --wildcards "*atlantiplex*" 2>/dev/null || echo "Note: Volume backup requires root or proper permissions"

# List backups
echo ""
echo "Backups in $BACKUP_DIR:"
ls -lh "$BACKUP_DIR" | tail -5

echo ""
echo "✓ Backup complete!"
