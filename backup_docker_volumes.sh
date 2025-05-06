#!/bin/bash

# Set the backup directory
BACKUP_DIR="./backups"

# Create the backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to backup a volume
backup_volume() {
    VOLUME_NAME=$1
    BACKUP_FILE="${BACKUP_DIR}/${VOLUME_NAME}_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

    echo "Backing up $VOLUME_NAME..."
    docker run --rm -v $VOLUME_NAME:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/$(basename $BACKUP_FILE) /data

    # Change ownership of the backup file
    sudo chown dockeradmin:dockeradmin $BACKUP_FILE

    echo "Backup of $VOLUME_NAME completed: $BACKUP_FILE"
}

# Backup each volume
backup_volume "caddy_data"
backup_volume "n8n_data"
backup_volume "n8n_n8n_storage"

echo "All backups completed."