"""
Texas RRC Refinery Statements PDF Scraper

This script scrapes PDF links from the Texas Railroad Commission (RRC) website
for refinery statements, downloads them locally, and uploads them to Databricks Volume.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import subprocess
from pathlib import Path


def scrape_pdf_links(url):
    """
    Scrape all PDF links from the given URL.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        list: A list of PDF URLs found on the page
    """
    try:
        # Send GET request to the URL
        print(f"Fetching page: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links on the page
        all_links = soup.find_all('a', href=True)
        
        # Filter for PDF links
        pdf_links = []
        for link in all_links:
            href = link['href']
            # Check if the link points to a PDF file
            if href.lower().endswith('.pdf'):
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(url, href)
                pdf_links.append(absolute_url)
        
        return pdf_links
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def download_pdf(pdf_url, local_dir):
    """
    Download a PDF file from a URL to a local directory.
    
    Args:
        pdf_url (str): The URL of the PDF to download
        local_dir (str): The local directory to save the PDF
        
    Returns:
        str: The local file path if successful, None otherwise
    """
    try:
        # Extract filename from URL
        filename = os.path.basename(pdf_url)
        local_path = os.path.join(local_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(local_path):
            print(f"  ✓ Already exists: {filename}")
            return local_path
        
        # Download the PDF
        print(f"  Downloading: {filename}...", end=" ")
        response = requests.get(pdf_url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Save to local file
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✓ Done")
        return local_path
    
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def upload_to_databricks_volume(local_dir, volume_path, profile='dev'):
    """
    Upload all files from local directory to Databricks Volume using Databricks CLI.
    
    Args:
        local_dir (str): The local directory containing files to upload
        volume_path (str): The Databricks Volume path (e.g., /Volumes/main/default/rrc_raw/)
        profile (str): The Databricks CLI profile to use (default: 'dev')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\nUploading files to Databricks Volume: {volume_path}")
        print(f"Using Databricks profile: {profile}")
        
        # Ensure the Volume directory exists
        print(f"  Ensuring directory exists...", end=" ")
        mkdir_result = subprocess.run(
            ['databricks', 'fs', 'mkdir', volume_path, '--profile', profile],
            capture_output=True,
            text=True
        )
        if mkdir_result.returncode == 0 or "already exists" in mkdir_result.stderr.lower():
            print("✓ Done")
        else:
            print(f"✗ Warning: {mkdir_result.stderr.strip()}")
        
        # Get all PDF files in the local directory
        pdf_files = [f for f in os.listdir(local_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("  No PDF files to upload.")
            return False
        
        success_count = 0
        for pdf_file in pdf_files:
            local_file_path = os.path.join(local_dir, pdf_file)
            remote_file_path = f"{volume_path.rstrip('/')}/{pdf_file}"
            
            print(f"  Uploading: {pdf_file}...", end=" ")
            
            # Use Databricks CLI to upload the file with profile
            # databricks fs cp <local-path> <dbfs-path> --profile <profile>
            result = subprocess.run(
                ['databricks', 'fs', 'cp', local_file_path, remote_file_path, '--overwrite', '--profile', profile],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Done")
                success_count += 1
            else:
                print(f"✗ Failed: {result.stderr.strip()}")
        
        print(f"\nSuccessfully uploaded {success_count}/{len(pdf_files)} files to Databricks Volume.")
        return success_count > 0
    
    except Exception as e:
        print(f"Error uploading to Databricks Volume: {e}")
        return False


def main():
    """Main function to run the scraper."""
    # Configuration
    target_url = "https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/refinery-statements/refineries-statements-2026/refinery-statements-2-2026/"
    local_download_dir = "./rrc_pdfs"
    databricks_volume_path = "/Volumes/workspace/default/rrc_raw/"
    
    print("=" * 80)
    print("Texas RRC Refinery Statements PDF Scraper")
    print("=" * 80)
    print()
    
    # Step 1: Scrape PDF links
    print("Step 1: Scraping PDF links from RRC website...")
    pdf_urls = scrape_pdf_links(target_url)
    
    print()
    print("=" * 80)
    print(f"Found {len(pdf_urls)} PDF link(s):")
    print("=" * 80)
    print()
    
    if not pdf_urls:
        print("No PDF links found on the page. Exiting.")
        return
    
    for i, pdf_url in enumerate(pdf_urls, 1):
        print(f"{i}. {pdf_url}")
    
    print()
    print("=" * 80)
    
    # Step 2: Create local directory and download PDFs
    print(f"\nStep 2: Downloading PDFs to local directory: {local_download_dir}")
    print("=" * 80)
    
    # Create local directory if it doesn't exist
    os.makedirs(local_download_dir, exist_ok=True)
    
    downloaded_files = []
    for pdf_url in pdf_urls:
        local_path = download_pdf(pdf_url, local_download_dir)
        if local_path:
            downloaded_files.append(local_path)
    
    print()
    print("=" * 80)
    print(f"Downloaded {len(downloaded_files)}/{len(pdf_urls)} PDF(s) successfully.")
    print("=" * 80)
    
    if not downloaded_files:
        print("No files were downloaded. Exiting.")
        return
    
    # Step 3: Upload to Databricks Volume
    print()
    print("Step 3: Uploading PDFs to Databricks Volume...")
    print("=" * 80)
    
    upload_success = upload_to_databricks_volume(local_download_dir, databricks_volume_path)
    
    print()
    print("=" * 80)
    if upload_success:
        print("✓ Process completed successfully!")
        print(f"  - PDFs downloaded to: {os.path.abspath(local_download_dir)}")
        print(f"  - PDFs uploaded to: {databricks_volume_path}")
    else:
        print("✗ Upload to Databricks Volume failed.")
        print(f"  - PDFs are available locally at: {os.path.abspath(local_download_dir)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
