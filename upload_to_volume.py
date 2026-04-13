"""
Upload files to Databricks Unity Catalog Volume using Python SDK
"""

import os
from databricks.sdk import WorkspaceClient
from pathlib import Path

def upload_files_to_volume():
    """Upload all PDF files to Unity Catalog Volume using Databricks SDK"""
    
    # Initialize Databricks client (uses profile from .databrickscfg)
    w = WorkspaceClient(profile='dev')
    
    # Configuration
    local_dir = "./rrc_pdfs"
    volume_path = "/Volumes/workspace/default/rrc_raw"
    
    print("=" * 80)
    print("Uploading files to Unity Catalog Volume using Python SDK")
    print("=" * 80)
    print(f"Local directory: {local_dir}")
    print(f"Volume path: {volume_path}")
    print()
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(local_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found to upload.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to upload")
    print()
    
    success_count = 0
    for pdf_file in pdf_files:
        local_file_path = os.path.join(local_dir, pdf_file)
        remote_file_path = f"{volume_path}/{pdf_file}"
        
        try:
            print(f"Uploading: {pdf_file}...", end=" ")
            
            # Upload using the Files API - pass file handle directly
            with open(local_file_path, 'rb') as f:
                w.files.upload(remote_file_path, f, overwrite=True)
            
            print("✓ Done")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    print()
    print("=" * 80)
    print(f"Successfully uploaded {success_count}/{len(pdf_files)} files")
    print("=" * 80)

if __name__ == "__main__":
    upload_files_to_volume()
