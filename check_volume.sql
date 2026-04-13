-- Check if the volume exists and its properties
DESCRIBE VOLUME EXTENDED workspace.default.rrc_raw;

-- List files in the volume using SQL
LIST '/Volumes/workspace/default/rrc_raw/';

-- Alternative: Show volumes in the schema
SHOW VOLUMES IN workspace.default;
