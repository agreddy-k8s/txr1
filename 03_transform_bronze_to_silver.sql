-- Transform bronze data to silver (normalized materials table)
-- This script explodes the materials_json array and creates one row per material per report

-- First, truncate silver table (or use MERGE for incremental)
TRUNCATE TABLE workspace.txrr1_silver.refinery_materials;

-- Insert normalized data from bronze to silver
INSERT INTO workspace.txrr1_silver.refinery_materials
SELECT
  -- Generate unique report ID
  CONCAT(
    COALESCE(registration_no, 'UNKNOWN'), '_',
    COALESCE(year, 'UNKNOWN'), '_',
    COALESCE(month, 'UNKNOWN')
  ) as report_id,
  
  -- Material information
  CAST(material.code AS INT) as material_code,
  material.name as material_name,
  
  -- Report metadata
  file_name,
  operator,
  refinery,
  registration_no,
  month as report_month,
  year as report_year,
  
  -- Material quantities (convert to DECIMAL)
  CAST(material.storage_beginning AS DECIMAL(18,2)) as storage_beginning,
  CAST(material.receipts AS DECIMAL(18,2)) as receipts,
  CAST(material.runs_to_stills AS DECIMAL(18,2)) as runs_to_stills,
  CAST(material.products_manufactured AS DECIMAL(18,2)) as products_manufactured,
  CAST(material.fuel_used AS DECIMAL(18,2)) as fuel_used,
  CAST(material.deliveries AS DECIMAL(18,2)) as deliveries,
  CAST(material.storage_end AS DECIMAL(18,2)) as storage_end,
  
  -- Data quality flags
  CASE WHEN material.code IS NULL THEN TRUE ELSE FALSE END as is_totals_row,
  
  -- Simple data quality score (100 if all required fields present, lower otherwise)
  CASE
    WHEN material.name IS NULL THEN 0
    WHEN material.storage_beginning IS NULL 
      AND material.receipts IS NULL 
      AND material.runs_to_stills IS NULL 
      AND material.products_manufactured IS NULL 
      AND material.deliveries IS NULL 
      AND material.storage_end IS NULL THEN 50
    ELSE 100
  END as data_quality_score,
  
  -- Audit fields
  CURRENT_TIMESTAMP() as created_timestamp,
  CURRENT_TIMESTAMP() as updated_timestamp

FROM workspace.txrr1_bronze.rrc_refinery_reports
LATERAL VIEW EXPLODE(FROM_JSON(materials_json, 'array<struct<
  name:string,
  code:int,
  storage_beginning:double,
  receipts:double,
  runs_to_stills:double,
  products_manufactured:double,
  fuel_used:double,
  deliveries:double,
  storage_end:double
>>')) materials_table AS material;

-- Show results
SELECT 
  'Total Reports' as metric,
  COUNT(DISTINCT report_id) as value
FROM workspace.txrr1_silver.refinery_materials
UNION ALL
SELECT 
  'Total Material Rows' as metric,
  COUNT(*) as value
FROM workspace.txrr1_silver.refinery_materials
UNION ALL
SELECT 
  'Rows with Quality Score 100' as metric,
  COUNT(*) as value
FROM workspace.txrr1_silver.refinery_materials
WHERE data_quality_score = 100
UNION ALL
SELECT 
  'TOTALS Rows' as metric,
  COUNT(*) as value
FROM workspace.txrr1_silver.refinery_materials
WHERE is_totals_row = TRUE;

-- Sample data
SELECT * FROM workspace.txrr1_silver.refinery_materials LIMIT 10;
