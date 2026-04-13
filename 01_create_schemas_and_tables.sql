-- Create bronze and silver schemas
CREATE SCHEMA IF NOT EXISTS workspace.txrr1_bronze
COMMENT 'Bronze layer - raw extracted data from RRC refinery reports';

CREATE SCHEMA IF NOT EXISTS workspace.txrr1_silver
COMMENT 'Silver layer - cleaned and validated refinery data';

-- Create bronze table for raw refinery report data
CREATE TABLE IF NOT EXISTS workspace.txrr1_bronze.rrc_refinery_reports (
  -- Metadata
  file_name STRING COMMENT 'Source PDF filename',
  extraction_timestamp TIMESTAMP COMMENT 'When the data was extracted',
  
  -- Header information
  form_type STRING,
  page_number STRING,
  revision STRING,
  corrected_report BOOLEAN,
  
  -- Report information
  report_title STRING,
  report_subtitle STRING,
  
  -- Operator information
  operator STRING,
  address_line1 STRING,
  address_line2 STRING,
  
  -- Period information
  month STRING,
  year STRING,
  registration_no STRING,
  refinery STRING,
  
  -- Materials data (stored as JSON string for flexibility)
  materials_json STRING COMMENT 'JSON array of all 25 material rows',
  
  -- Stamp information
  stamp_received_by STRING,
  stamp_date STRING,
  stamp_location STRING,
  
  -- Certificate information
  certificate_signed_by STRING,
  certificate_date_signed STRING,
  certificate_title STRING,
  certificate_telephone STRING,
  
  -- Full extracted JSON for reference
  raw_json STRING COMMENT 'Complete extracted JSON'
)
COMMENT 'Bronze table containing raw extracted data from RRC refinery PDF reports';

-- Create silver table with normalized materials data
CREATE TABLE IF NOT EXISTS workspace.txrr1_silver.refinery_materials (
  -- Keys
  report_id STRING COMMENT 'Unique identifier: {registration_no}_{year}_{month}',
  material_code INT COMMENT 'Material code (1-24, null for TOTALS)',
  material_name STRING,
  
  -- Report metadata
  file_name STRING,
  operator STRING,
  refinery STRING,
  registration_no STRING,
  report_month STRING,
  report_year STRING,
  
  -- Material quantities (in barrels)
  storage_beginning DECIMAL(18,2),
  receipts DECIMAL(18,2),
  runs_to_stills DECIMAL(18,2),
  products_manufactured DECIMAL(18,2),
  fuel_used DECIMAL(18,2),
  deliveries DECIMAL(18,2),
  storage_end DECIMAL(18,2),
  
  -- Data quality flags
  is_totals_row BOOLEAN,
  data_quality_score DECIMAL(5,2) COMMENT 'Quality score based on validation rules',
  
  -- Audit fields
  created_timestamp TIMESTAMP,
  updated_timestamp TIMESTAMP
)
COMMENT 'Silver table with normalized refinery materials data';

-- Show created objects
SHOW SCHEMAS IN workspace LIKE 'txrr1%';
SHOW TABLES IN workspace.txrr1_bronze;
SHOW TABLES IN workspace.txrr1_silver;
