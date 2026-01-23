#!/usr/bin/env python3
import json
import logging
import pandas as pd
from pathlib import Path
from pygbif import occurrences
from gbif_config import DATA_DIR, SPECIES, LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def finish_download(download_key):
    data_dir = DATA_DIR
    data_dir.mkdir(exist_ok=True)
    
    logging.info(f"Finishing processing for download key: {download_key}")
    
    # Get metadata from GBIF
    logging.info("Fetching metadata from GBIF...")
    citation_info = occurrences.download_meta(download_key)
    doi = citation_info.get('doi')
    logging.info(f"DOI: {doi}")
    
    # The file is already on disk from previous failed run
    zip_path = Path(f"{download_key}.zip")
    if not zip_path.exists():
        logging.info("Zip file not found locally, downloading...")
        download_info = occurrences.download_get(download_key)
        if isinstance(download_info, dict) and 'path' in download_info:
            zip_path = Path(download_info['path'])
    
    # Read the data (handling tab separator in the zip)
    # Actually, pygbif might have unzipped it? No, it usually returns the zip path.
    # In my previous run, it said "On disk at ./0005649-260120142942310.zip"
    
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        csv_filename = csv_files[0]
        with zip_ref.open(csv_filename) as f:
            df = pd.read_csv(f, sep='\t')
    
    logging.info(f"Loaded {len(df)} records")
    
    # Save combined file
    combined_file = data_dir / "all_species_occurrences.csv"
    df.to_csv(combined_file, index=False)
    logging.info(f"Saved to {combined_file}")
    
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
        f.write(f"GBIF.org (23 January 2026) GBIF Occurrence Download {doi}\n")
        f.write("```\n\n")
        f.write("## Download Information\n\n")
        f.write(f"- **DOI**: [{doi}](https://doi.org/{doi.replace('doi:', '') if doi else ''})\n")
        f.write(f"- **Download URL**: [https://www.gbif.org/occurrence/download/{download_key}](https://www.gbif.org/occurrence/download/{download_key})\n")
        f.write(f"- **Download Key**: {download_key}\n")
        f.write(f"- **Total Records**: {len(df)} occurrence records\n")
        f.write(f"- **Download Date**: 23 January 2026\n\n")
        f.write("## Data Usage Terms\n\n")
        f.write("This data is subject to the [GBIF Data Use Agreement](https://www.gbif.org/terms).\n\n")
        f.write("## Citation Guidelines\n\n")
        f.write("When using this data, please cite both GBIF and the original data providers.\n\n")
        f.write("## Species Included\n\n")
        for species in SPECIES:
            f.write(f"- {species}\n")
    
    # Create summary
    summary = {
        'total_species': len(SPECIES),
        'total_records': len(df) if not df.empty else 0,
        'download_key': download_key,
        'doi': doi,
        'status': 'SUCCEEDED',
        'files': {
            'combined_data': str(combined_file),
            'citation_json': str(citation_file),
            'citation_md': str(citation_md)
        }
    }
    
    summary_file = data_dir / 'download_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logging.info("Processing complete!")

if __name__ == "__main__":
    finish_download("0005649-260120142942310")
