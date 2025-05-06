#!/bin/bash

# Set the backup directory
BACKUP_DIR="./backups"

# Get current date/time for subfolder
DATETIME=$(date +%Y%m%d_%H%M%S)
BACKUP_SUBDIR="${BACKUP_DIR}/${DATETIME}"

# Create the backup directory and subfolder if they don't exist
mkdir -p $BACKUP_SUBDIR

# Run the n8n command and save the output to the credentials.json file
docker-compose run --rm --entrypoint="" n8n n8n export:credentials --all --decrypted > "${BACKUP_SUBDIR}/credentials.json"

# Print a message indicating the backup was successful
echo "Credentials backup completed: ${BACKUP_SUBDIR}/credentials.json"

# Run the n8n command and save the output to the workflows.json file
docker-compose run --rm --entrypoint="" n8n n8n export:workflow --all > "${BACKUP_SUBDIR}/workflows.json"

# Print a message indicating the backup was successful
echo "Workflows backup completed: ${BACKUP_SUBDIR}/workflows.json"

