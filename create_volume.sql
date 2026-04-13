-- Create the volume in the correct workspace catalog
CREATE VOLUME IF NOT EXISTS workspace.default.rrc_raw;

-- Verify the volume was created
DESCRIBE VOLUME workspace.default.rrc_raw;
