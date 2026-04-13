# RRC Refinery Reports Data Pipeline

This pipeline extracts data from Texas RRC refinery PDF reports and loads it into Databricks bronze and silver tables.

## Architecture

```
PDF Files (Volume) → Bronze Table (Raw JSON) → Silver Table (Normalized)
```

## Setup Instructions

### 1. Create Schemas and Tables

Run the SQL file in Databricks SQL Warehouse or Notebook:

```sql
-- File: 01_create_schemas_and_tables.sql
```

This creates:
- `workspace.txrr1_bronze` schema
- `workspace.txrr1_silver` schema
- `workspace.txrr1_bronze.rrc_refinery_reports` table
- `workspace.txrr1_silver.refinery_materials` table

### 2. Set Environment Variables

Before running the extraction script, set these environment variables:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
$env:DATABRICKS_WAREHOUSE_ID="your-warehouse-id"
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=your-anthropic-api-key
set DATABRICKS_WAREHOUSE_ID=your-warehouse-id
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"
```

To find your Databricks Warehouse ID:
1. Go to Databricks SQL Warehouses
2. Click on your warehouse
3. Copy the ID from the URL or warehouse details

### 3. Run PDF Extraction

Extract data from PDFs and load into bronze table:

```bash
python 02_extract_pdfs_to_bronze.py
```

This script:
- Reads all PDFs from `./rrc_pdfs/` directory
- Uses Claude AI to extract structured data from first page
- Inserts extracted data into bronze table
- Processes 22 PDF files

### 4. Transform to Silver

Run the transformation SQL in Databricks:

```sql
-- File: 03_transform_bronze_to_silver.sql
```

This:
- Explodes the materials JSON array
- Creates one row per material per report (25 materials × 22 reports = 550 rows)
- Calculates data quality scores
- Normalizes data for analytics

## Data Model

### Bronze Table: `workspace.txrr1_bronze.rrc_refinery_reports`

One row per PDF file with all extracted data:
- Metadata (file_name, extraction_timestamp)
- Header info (form_type, page_number, revision)
- Report info (title, subtitle)
- Operator info (operator, address)
- Period info (month, year, registration_no, refinery)
- Materials data (JSON array of 25 materials)
- Stamp info (received_by, date, location)
- Certificate info (signed_by, date_signed, title, telephone)
- Raw JSON (complete extraction)

### Silver Table: `workspace.txrr1_silver.refinery_materials`

Normalized table with one row per material per report:
- Keys (report_id, material_code, material_name)
- Report metadata (file_name, operator, refinery, etc.)
- Material quantities (storage_beginning, receipts, runs_to_stills, etc.)
- Data quality flags (is_totals_row, data_quality_score)
- Audit fields (created_timestamp, updated_timestamp)

## Materials List

The pipeline extracts data for 24 materials plus TOTALS:

1. Propane
2. Butane
3. Butane-Propane
4. Motor Gasoline
5. Kerosene
6. Home Heating Oil
7. Diesel Fuel
8. Other Middle Distillates
9. Aviation Gasoline
10. Kerosene-Type Jet Fuel
11. Naptha-Type Jet Fuel
12. Fuel Oil #4 For Utility Use
13. Fuel Oils #5 #6 For Utility Use
14. Fuel Oil #4 for Non-Utility Use
15. Fuel Oils #5 #6 for Non-Utility Use
16. Bunker C
17. Navy Special
18. Other Residual Fuels
19. Petrochemical Feedstocks
20. Lubricants
21. Special Napthas
22. Solvent Products
23. Miscellaneous
24. Crude Oil
25. TOTALS (summary row)

## Files

- `01_create_schemas_and_tables.sql` - DDL for schemas and tables
- `02_extract_pdfs_to_bronze.py` - Python script for PDF extraction using Claude AI
- `03_transform_bronze_to_silver.sql` - SQL transformation from bronze to silver
- `upload_to_volume.py` - Upload PDFs to Databricks Volume
- `rrc_scraper.py` - Scrape and download PDFs from RRC website

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
**Solution:** Set the environment variable before running the script

### Issue: "DATABRICKS_WAREHOUSE_ID not set"
**Solution:** Get your warehouse ID from Databricks and set the environment variable

### Issue: "Failed to insert into bronze table"
**Solution:** Check that the schemas and tables were created successfully

### Issue: "Files not visible in Databricks UI"
**Solution:** Use `upload_to_volume.py` instead of CLI to upload files

## Next Steps

After loading data into silver:
1. Create gold layer aggregations
2. Build dashboards and reports
3. Set up scheduled jobs for new data
4. Add data quality checks and alerts
