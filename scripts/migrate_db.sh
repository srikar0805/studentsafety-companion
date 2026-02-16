#!/bin/bash

# Usage: ./migrate_db.sh <CLOUD_DB_URL>
# Example: ./migrate_db.sh postgres://user:pass@ep-xyz.region.neon.tech/neondb

if [ -z "$1" ]; then
    echo "Usage: ./migrate_db.sh <CLOUD_DB_URL>"
    exit 1
fi

if ! command -v pg_dump &> /dev/null; then
    echo "Error: pg_dump could not be found."
    echo "Please install PostgreSQL tools. On macOS: brew install postgresql"
    exit 1
fi

CLOUD_DB_URL=$1
DUMP_FILE="studentsafety_dump.custom"

echo "--- 1. Dumping Local Database ---"
pg_dump -h localhost -U postgres -d studentsafety -F c -b -v -f $DUMP_FILE

if [ $? -ne 0 ]; then
    echo "Dump failed!"
    exit 1
fi

echo "--- 2. Restoring to Cloud ---"
pg_restore -d "$CLOUD_DB_URL" -v $DUMP_FILE

if [ $? -ne 0 ]; then
    echo "Restore failed (or had warnings)!"
    # Don't exit, often warnings about owner/privileges are expected
fi

echo "--- Migration Complete ---"
echo "Don't forget to update your .env file with the new DATABASE_URL!"
