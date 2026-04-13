"""
Extract data from RRC refinery PDF reports using Claude AI and load into bronze table
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
import anthropic
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DATABRICKS_PROFILE = "dev"
VOLUME_PATH = "/Volumes/workspace/default/rrc_raw"
BRONZE_TABLE = "workspace.txrr1_bronze.rrc_refinery_reports"

# Extraction prompt
EXTRACTION_PROMPT = """Extract ALL data from this refinery report first page into a JSON object with these sections:

1. "header": object with form_type, page_number, revision, corrected_report (boolean)
2. "report_info": object with report_title, report_subtitle
3. "operator_info": object with operator, address_line1, address_line2
4. "period_info": object with month, year, registration_no, refinery
5. "materials_table": array of ALL 24 material rows PLUS the TOTALS row (25 rows total).
   Each row must have: name (string), code (int or null for TOTALS), storage_beginning (number or null), 
   receipts (number or null), runs_to_stills (number or null), products_manufactured (number or null), 
   fuel_used (number or null), deliveries (number or null), storage_end (number or null).
   IMPORTANT: Include ALL rows even if all numeric values are null. The materials are:
   Propane(1), Butane(2), Butane-Propane(3), Motor Gasoline(4), Kerosene(5), Home Heating Oil(6),
   Diesel Fuel(7), Other Middle Distillates(8), Aviation Gasoline(9), Kerosene-Type Jet Fuel(10),
   Naptha-Type Jet Fuel(11), Fuel Oil #4 For Utility Use(12), Fuel Oils #5 #6 For Utility Use(13),
   Fuel Oil #4 for Non-Utility Use(14), Fuel Oils #5 #6 for Non-Utility Use(15), Bunker C(16),
   Navy Special(17), Other Residual Fuels(18), Petrochemical Feedstocks(19), Lubricants(20),
   Special Napthas(21), Solvent Products(22), Miscellaneous(23), Crude Oil(24), TOTALS.
6. "stamp": object with received_by, date, location. This stamp/seal is optional. If you find it extract and if not, capture as null.
7. "certificate": object with signed_by, date_signed, title, telephone

IMPORTANT: Remove commas from numbers. Return ONLY valid JSON, no explanation or markdown."""


def extract_pdf_with_claude(pdf_path: str) -> dict:
    """Extract data from PDF using Claude AI"""
    print(f"  Extracting data from: {os.path.basename(pdf_path)}")
    
    # Read PDF file
    with open(pdf_path, 'rb') as f:
        pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')
    
    # Initialize Claude client
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Call Claude API with PDF
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    # Parse response
    response_text = message.content[0].text
    
    # Clean response (remove markdown if present)
    if response_text.startswith("```json"):
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif response_text.startswith("```"):
        response_text = response_text.split("```")[1].split("```")[0].strip()
    
    # Parse JSON
    extracted_data = json.loads(response_text)
    
    return extracted_data


def insert_into_bronze(w: WorkspaceClient, file_name: str, extracted_data: dict):
    """Insert extracted data into bronze table"""
    
    # Prepare data for insertion
    header = extracted_data.get('header', {})
    report_info = extracted_data.get('report_info', {})
    operator_info = extracted_data.get('operator_info', {})
    period_info = extracted_data.get('period_info', {})
    stamp = extracted_data.get('stamp', {})
    certificate = extracted_data.get('certificate', {})
    materials_json = json.dumps(extracted_data.get('materials_table', []))
    raw_json = json.dumps(extracted_data)
    
    # Escape single quotes for SQL
    def escape_sql(value):
        if value is None:
            return 'NULL'
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, str):
            return f"'{value.replace(chr(39), chr(39)+chr(39))}'"
        return f"'{value}'"
    
    # Build INSERT statement
    sql = f"""
    INSERT INTO {BRONZE_TABLE} VALUES (
        {escape_sql(file_name)},
        CURRENT_TIMESTAMP(),
        {escape_sql(header.get('form_type'))},
        {escape_sql(header.get('page_number'))},
        {escape_sql(header.get('revision'))},
        {escape_sql(header.get('corrected_report'))},
        {escape_sql(report_info.get('report_title'))},
        {escape_sql(report_info.get('report_subtitle'))},
        {escape_sql(operator_info.get('operator'))},
        {escape_sql(operator_info.get('address_line1'))},
        {escape_sql(operator_info.get('address_line2'))},
        {escape_sql(period_info.get('month'))},
        {escape_sql(period_info.get('year'))},
        {escape_sql(period_info.get('registration_no'))},
        {escape_sql(period_info.get('refinery'))},
        {escape_sql(materials_json)},
        {escape_sql(stamp.get('received_by'))},
        {escape_sql(stamp.get('date'))},
        {escape_sql(stamp.get('location'))},
        {escape_sql(certificate.get('signed_by'))},
        {escape_sql(certificate.get('date_signed'))},
        {escape_sql(certificate.get('title'))},
        {escape_sql(certificate.get('telephone'))},
        {escape_sql(raw_json)}
    )
    """
    
    # Execute SQL
    response = w.statement_execution.execute_statement(
        warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID"),
        statement=sql,
        catalog="workspace",
        schema="txrr1_bronze"
    )
    
    # Wait for completion
    statement_id = response.statement_id
    while True:
        status = w.statement_execution.get_statement(statement_id)
        if status.status.state in [StatementState.SUCCEEDED, StatementState.FAILED, StatementState.CANCELED]:
            break
    
    if status.status.state == StatementState.SUCCEEDED:
        print(f"    ✓ Inserted into bronze table")
    else:
        print(f"    ✗ Failed to insert: {status.status.error}")
        raise Exception(f"SQL execution failed: {status.status.error}")


def main():
    """Main extraction pipeline"""
    print("=" * 80)
    print("RRC Refinery PDF Extraction Pipeline")
    print("=" * 80)
    print()
    
    # Check for API key
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return
    
    # Check for warehouse ID
    if not os.getenv("DATABRICKS_WAREHOUSE_ID"):
        print("ERROR: DATABRICKS_WAREHOUSE_ID environment variable not set")
        print("Please set it with: export DATABRICKS_WAREHOUSE_ID='your-warehouse-id'")
        return
    
    # Initialize Databricks client
    w = WorkspaceClient(profile=DATABRICKS_PROFILE)
    
    # Get list of PDFs from local directory
    local_pdf_dir = "./rrc_pdfs"
    pdf_files = sorted([f for f in os.listdir(local_pdf_dir) if f.endswith('.pdf')])
    
    print(f"Found {len(pdf_files)} PDF files to process")
    print()
    
    success_count = 0
    failed_files = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file}")
        
        try:
            # Extract data
            pdf_path = os.path.join(local_pdf_dir, pdf_file)
            extracted_data = extract_pdf_with_claude(pdf_path)
            
            # Insert into bronze
            insert_into_bronze(w, pdf_file, extracted_data)
            
            success_count += 1
            print()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            failed_files.append(pdf_file)
            print()
    
    # Summary
    print("=" * 80)
    print(f"Extraction Complete: {success_count}/{len(pdf_files)} successful")
    if failed_files:
        print(f"Failed files: {', '.join(failed_files)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
