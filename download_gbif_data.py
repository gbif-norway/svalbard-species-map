#!/usr/bin/env python3
"""
GBIF Data Download Pipeline for Svalbard Species Map

This script downloads occurrence data from GBIF for specific marine species
with location precision within 20km using the GBIF download API to get a unique DOI.
"""

import os
import json
import time
from pathlib import Path
import pandas as pd
from pygbif import occurrences
from tqdm import tqdm
import logging
from gbif_config import (
    GBIF_USERNAME, 
    GBIF_PASSWORD, 
    SPECIES, 
    DATA_DIR, 
    LOGS_DIR,
    DOWNLOAD_FORMAT,
    validate_config,
    get_download_params
)

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'gbif_download.log'),
        logging.StreamHandler()
    ]
)

def create_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR

def get_species_key(species_name):
    """Get GBIF species key for a given species name."""
    try:
        # Search for the species
        result = occurrences.search(
            q=species_name,
            limit=1
        )
        
        if result['results']:
            return result['results'][0]['speciesKey']
        else:
            logging.warning(f"No species key found for: {species_name}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting species key for {species_name}: {e}")
        return None

def download_all_species_with_doi(data_dir):
    """Download data for all species and create a combined dataset with DOI."""
    logging.info("Creating combined download for all species to get a single DOI")
    
    # Check if data is already downloaded
    combined_file = data_dir / "all_species_occurrences.csv"
    citation_file = data_dir / "gbif_citation.json"
    summary_file = data_dir / 'download_summary.json'
    
    if combined_file.exists() and citation_file.exists() and summary_file.exists():
        logging.info("Data already downloaded and ready!")
        logging.info(f"Combined data available at: {combined_file}")
        logging.info(f"Citation info available at: {citation_file}")
        logging.info(f"Summary available at: {summary_file}")
        return combined_file
    
    # Validate configuration
    if not validate_config():
        logging.error("GBIF credentials not configured. Please update gbif_config.py")
        return None
    
    # Create a combined download request for all species
    species_keys = []
    for species in SPECIES:
        species_key = get_species_key(species)
        if species_key:
            species_keys.append(species_key)
            logging.info(f"Found species key for {species}: {species_key}")
        else:
            logging.error(f"Could not get species key for {species}")
    
    if not species_keys:
        logging.error("No valid species keys found")
        return None
    
    try:
        # Get download parameters from config
        queries = get_download_params(species_keys)
        
        # Create download request
        result = occurrences.download(
            queries,
            format=DOWNLOAD_FORMAT,
            user=GBIF_USERNAME,
            pwd=GBIF_PASSWORD,
            email=True
        )
        if isinstance(result, tuple):
            download_key = result[0]
        else:
            download_key = result
        
        logging.info(f"Combined download request created with key: {download_key}")
        
        # Wait for download to be ready
        status = 'RUNNING'
        max_wait_time = 3600  # 1 hour timeout
        start_time = time.time()
        
        while status in ['RUNNING', 'PREPARING']:
            if time.time() - start_time > max_wait_time:
                logging.error("Download timeout after 1 hour")
                return None
                
            status_info = occurrences.download_meta(download_key)
            status = status_info['status']
            logging.info(f"Download status: {status}")
            
            if status == 'SUCCEEDED':
                break
            elif status == 'FAILED':
                logging.error("Download failed")
                return None
            
            time.sleep(30)  # Wait 30 seconds before checking again
        
        # Download the file
        if status == 'SUCCEEDED':
            download_info = occurrences.download_get(download_key)
            
            # Check if download_info is a dictionary and has a link or path
            if isinstance(download_info, dict):
                if 'downloadLink' in download_info:
                    download_source = download_info['downloadLink']
                elif 'path' in download_info:
                    download_source = download_info['path']
                else:
                    logging.error(f"Download info missing both link and path: {download_info}")
                    return None
            else:
                logging.error(f"Unexpected download info format: {type(download_info)}")
                return None
            
            # Read the CSV data
            df = pd.read_csv(download_source, sep='\t' if download_source.endswith('.csv') else ',')
            
            # Save combined file
            combined_file = data_dir / "all_species_occurrences.csv"
            df.to_csv(combined_file, index=False)
            logging.info(f"Downloaded {len(df)} total records")
            
            # Get citation information
            citation_info = occurrences.download_meta(download_key)
            
            # Save citation info
            citation_file = data_dir / "gbif_citation.json"
            with open(citation_file, 'w') as f:
                json.dump(citation_info, f, indent=2)
            
            # Create citation markdown
            citation_md = data_dir / "CITATION.md"
            with open(citation_md, 'w') as f:
                f.write("# GBIF Data Citation Information\n\n")
                f.write("## GBIF Citation\n\n")
                f.write("When using this data, please cite GBIF:\n\n")
                f.write("```\n")
                if 'doi' in citation_info:
                    f.write(f"GBIF.org (2024) GBIF Occurrence Download {citation_info['doi']}\n")
                else:
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
                f.write(f"\n## Download Key\n\n{download_key}\n")
                if 'doi' in citation_info:
                    f.write(f"\n## DOI\n\n{citation_info['doi']}\n")
            
            # Create summary
            summary = {
                'total_species': len(SPECIES),
                'species_keys': species_keys,
                'total_records': len(df),
                'download_key': download_key,
                'doi': citation_info.get('doi'),
                'created': citation_info.get('created'),
                'status': status,
                'files': {
                    'combined_data': str(combined_file),
                    'citation_json': str(citation_file),
                    'citation_md': str(citation_md)
                }
            }
            
            summary_file = data_dir / 'download_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logging.info(f"Combined data saved to {combined_file}")
            logging.info(f"Citation info saved to {citation_file} and {citation_md}")
            logging.info(f"Summary saved to {summary_file}")
            
            if 'doi' in citation_info:
                logging.info(f"DOI assigned: {citation_info['doi']}")
            
            return combined_file
            
    except Exception as e:
        logging.error(f"Error creating combined download: {e}")
        return None

def main():
    """Main function to download data for all species."""
    logging.info("Starting GBIF data download pipeline with DOI")
    
    # Create data directory
    data_dir = create_data_directory()
    
    # Download combined dataset with DOI
    combined_file = download_all_species_with_doi(data_dir)
    
    if combined_file:
        logging.info("Download complete with DOI!")
        logging.info(f"Combined data saved to: {combined_file}")
        logging.info("Citation information saved to: data/gbif_citation.json and data/CITATION.md")
        
        # Generate species distribution maps
        logging.info("Starting species distribution map generation...")
        try:
            from generate_species_maps import generate_all_species_maps
            if generate_all_species_maps():
                logging.info("Species distribution maps generated successfully!")
                logging.info("Maps saved in: data/maps/")
            else:
                logging.warning("Failed to generate species distribution maps")
        except ImportError as e:
            logging.error(f"Could not import map generation module: {e}")
            logging.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
        except Exception as e:
            logging.error(f"Error generating maps: {e}")
    else:
        logging.error("Download failed")

if __name__ == "__main__":
    main() 