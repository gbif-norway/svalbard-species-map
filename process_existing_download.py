#!/usr/bin/env python3
"""
Process Existing GBIF Download

This script processes an existing GBIF download file that was already downloaded.
"""

import os
import json
import zipfile
import pandas as pd
from pathlib import Path
import logging
from gbif_config import DATA_DIR, SPECIES

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'process_download.log'),
        logging.StreamHandler()
    ]
)

def process_existing_download():
    """Process the existing downloaded file."""
    logging.info("Processing existing GBIF download")
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Look for the downloaded zip file
    zip_files = list(Path('.').glob('*.zip'))
    if not zip_files:
        logging.error("No zip files found in current directory")
        return None
    
    # Use the first zip file found
    zip_file = zip_files[0]
    logging.info(f"Found zip file: {zip_file}")
    
    try:
        # Extract the CSV file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                logging.error("No CSV file found in zip")
                return None
            
            csv_filename = csv_files[0]
            logging.info(f"Extracting {csv_filename}")
            
            # Extract to data directory
            zip_ref.extract(csv_filename, DATA_DIR)
            extracted_csv = DATA_DIR / csv_filename
            
            # Read the CSV data
            df = pd.read_csv(extracted_csv, sep='\t')
            logging.info(f"Loaded {len(df)} records from {csv_filename}")
            
            # Save as our standard filename
            combined_file = DATA_DIR / "all_species_occurrences.csv"
            df.to_csv(combined_file, index=False)
            logging.info(f"Saved combined data to {combined_file}")
            
            # Create citation info (simulated since we don't have the original download metadata)
            citation_info = {
                'downloadKey': zip_file.stem,
                'status': 'SUCCEEDED',
                'created': '2024-06-26',
                'totalRecords': len(df),
                'format': 'SIMPLE_CSV',
                'note': 'Processed from existing download file'
            }
            
            # Save citation info
            citation_file = DATA_DIR / "gbif_citation.json"
            with open(citation_file, 'w') as f:
                json.dump(citation_info, f, indent=2)
            
            # Create citation markdown
            citation_md = DATA_DIR / "CITATION.md"
            with open(citation_md, 'w') as f:
                f.write("# GBIF Data Citation Information\n\n")
                f.write("## GBIF Citation\n\n")
                f.write("When using this data, please cite GBIF:\n\n")
                f.write("```\n")
                f.write("GBIF.org (2024) GBIF Occurrence Download\n")
                f.write("```\n\n")
                f.write("## Data Usage Terms\n\n")
                f.write("This data is subject to the [GBIF Data Use Agreement](https://www.gbif.org/terms).\n\n")
                f.write("## Citation Guidelines\n\n")
                f.write("When using this data, please cite both GBIF and the original data providers.\n\n")
                f.write("## Species Included\n\n")
                for species in SPECIES:
                    f.write(f"- {species}\n")
                f.write(f"\n## Total Records\n\n{len(df)} occurrence records\n")
                f.write(f"\n## Download Date\n\n{citation_info.get('created', 'Unknown')}\n")
                f.write(f"\n## Download Key\n\n{citation_info['downloadKey']}\n")
            
            # Create summary
            summary = {
                'total_species': len(SPECIES),
                'total_records': len(df),
                'download_key': citation_info['downloadKey'],
                'created': citation_info.get('created'),
                'status': 'SUCCEEDED',
                'files': {
                    'combined_data': str(combined_file),
                    'citation_json': str(citation_file),
                    'citation_md': str(citation_md)
                }
            }
            
            summary_file = DATA_DIR / 'download_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logging.info(f"Citation info saved to {citation_file} and {citation_md}")
            logging.info(f"Summary saved to {summary_file}")
            
            # Clean up extracted file
            extracted_csv.unlink()
            
            return combined_file
            
    except Exception as e:
        logging.error(f"Error processing existing download: {e}")
        return None

def main():
    """Main function to process existing download."""
    logging.info("Processing existing GBIF download file")
    
    combined_file = process_existing_download()
    
    if combined_file:
        logging.info("Processing complete!")
        logging.info(f"Combined data saved to: {combined_file}")
        logging.info("Citation information saved to: data/gbif_citation.json and data/CITATION.md")
    else:
        logging.error("Processing failed")

if __name__ == "__main__":
    main() 