@echo off
REM Script to apply CoMo Transit database migrations
echo Applying CoMo Transit schema migration...
psql -U postgres -d campus_safety -f src\db\migrations\como_transit_schema.sql

echo.
echo Populating CoMo Transit data...
psql -U postgres -d campus_safety -f src\db\data\como_transit_data.sql

echo.
echo Migration complete!
pause
