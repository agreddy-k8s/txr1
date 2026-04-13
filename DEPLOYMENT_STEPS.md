# Deployment Steps (No Git Required)

Follow these steps to deploy and run the pipeline manually.

## Step 1: Create Schemas and Tables in Databricks

### Option A: Using Databricks SQL Editor
1. Open Databricks workspace in your browser
2. Go to **SQL Editor** (or **SQL Workspace**)
3. Open the file `01_create_schemas_and_tables.sql` from your local machine
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click **Run** (or press Ctrl+Enter)
7. Verify schemas and tables are created

### Option B: Using Databricks Notebook
1. In Databricks, go to **Workspace**
2. Click **Create** → **Notebook**
3. Name it: `01_Create_Schemas_and_Tables`
4. In the first cell, paste the contents of `01_create_schemas_and_tables.sql`
5. Change cell type to **SQL** (dropdown at top of cell)
6. Run the cell
7. Verify output shows schemas and tables created

---

## Step 2: Set Up Environment Variables

You need two environment variables for the Python extraction script:

### Get Your Databricks Warehouse ID:
1. In Databricks, go to **SQL Warehouses**
2. Click on your warehouse (or create one if needed)
3. Look at the URL - it will be like: `https://your-workspace.databricks.com/sql/warehouses/abc123def456`
4. Copy the ID after `/warehouses/` (e.g., `abc123def456`)

### Get Your Anthropic API Key:
1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Go to **API Keys**
4. Create a new key or copy existing one

### Set the Variables (Windows PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
$env:DATABRICKS_WAREHOUSE_ID="your-warehouse-id-here"
```

### Set the Variables (Windows CMD):
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
set DATABRICKS_WAREHOUSE_ID=your-warehouse-id-here
```

**IMPORTANT:** Keep this terminal window open for the next step!

---

## Step 3: Run the PDF Extraction Script

In the **same terminal window** where you set the environment variables:

```bash
python 02_extract_pdfs_to_bronze.py
```

This will:
- Process all 22 PDF files from `./rrc_pdfs/`
- Extract data using Claude AI
- Insert into `workspace.txrr1_bronze.rrc_refinery_reports` table
- Take approximately 5-10 minutes (depending on API speed)

**Expected Output:**
```
================================================================================
RRC Refinery PDF Extraction Pipeline
================================================================================

Found 22 PDF files to process

[1/22] Processing: 2026-february-01-0692.pdf
  Extracting data from: 2026-february-01-0692.pdf
    ✓ Inserted into bronze table

[2/22] Processing: 2026-february-02-0057.pdf
...
```

---

## Step 4: Verify Bronze Data

### Check the data in Databricks:

1. Go to **SQL Editor** or create a new **Notebook**
2. Run this query:

```sql
-- Check how many records were loaded
SELECT COUNT(*) as total_records 
FROM workspace.txrr1_bronze.rrc_refinery_reports;

-- View sample data
SELECT 
  file_name,
  operator,
  refinery,
  month,
  year,
  registration_no
FROM workspace.txrr1_bronze.rrc_refinery_reports
LIMIT 10;
```

You should see 22 records (one per PDF file).

---

## Step 5: Transform Bronze to Silver

### Option A: Using Databricks SQL Editor
1. Open the file `03_transform_bronze_to_silver.sql` from your local machine
2. Copy the entire contents
3. Paste into SQL Editor
4. Click **Run**
5. Review the summary metrics at the end

### Option B: Using Databricks Notebook
1. Create a new notebook: `03_Transform_Bronze_to_Silver`
2. Paste the contents of `03_transform_bronze_to_silver.sql`
3. Change cell type to **SQL**
4. Run the cell

**Expected Output:**
```
metric                          | value
--------------------------------|------
Total Reports                   | 22
Total Material Rows             | 550
Rows with Quality Score 100     | ~500
TOTALS Rows                     | 22
```

---

## Step 6: Verify Silver Data

Run this query to verify the silver table:

```sql
-- Check silver table
SELECT 
  report_id,
  material_code,
  material_name,
  operator,
  refinery,
  storage_beginning,
  receipts,
  deliveries,
  storage_end
FROM workspace.txrr1_silver.refinery_materials
WHERE material_code = 4  -- Motor Gasoline
ORDER BY report_year, report_month
LIMIT 10;
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
- Make sure you set the environment variable in the terminal
- Run the Python script in the **same terminal window**
- Don't close the terminal between setting variables and running the script

### Issue: "DATABRICKS_WAREHOUSE_ID not set"
- Get the warehouse ID from Databricks SQL Warehouses
- Set the environment variable before running the script

### Issue: "Table not found"
- Make sure Step 1 completed successfully
- Check that schemas exist: `SHOW SCHEMAS IN workspace LIKE 'txrr1%';`

### Issue: "No PDF files found"
- Make sure you're running the script from the `c:\Users\gopal.allam\txr1` directory
- Verify `./rrc_pdfs/` folder exists with PDF files

### Issue: Python script fails with import errors
- Install required packages:
  ```bash
  pip install anthropic databricks-sdk
  ```

---

## Summary

✅ **Step 1:** Create schemas and tables (SQL in Databricks)  
✅ **Step 2:** Set environment variables (Terminal)  
✅ **Step 3:** Run extraction script (Python locally)  
✅ **Step 4:** Verify bronze data (SQL in Databricks)  
✅ **Step 5:** Transform to silver (SQL in Databricks)  
✅ **Step 6:** Verify silver data (SQL in Databricks)  

**Total Time:** ~15-20 minutes

---

## What's Next?

After completing these steps, you'll have:
- 22 records in bronze table (raw extracted data)
- 550 records in silver table (normalized materials data)
- Ready for analytics, dashboards, and reporting!

You can now:
1. Create visualizations in Databricks SQL dashboards
2. Build additional gold layer aggregations
3. Set up scheduled jobs to process new PDFs automatically
4. Export data for use in other tools
