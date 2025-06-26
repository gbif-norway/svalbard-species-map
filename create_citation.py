#!/usr/bin/env python3
"""
Create citation information for downloaded GBIF data
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def create_citation_files():
    """Create citation files for the downloaded GBIF data."""
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("Data directory not found. Please run the download pipeline first.")
        return
    
    # Species list
    species = [
        "Calanus finmarchicus",
        "Calanus glacialis", 
        "Parasagitta elegans",
        "Semibalanus balanoides",
        "Oithona similis",
        "Catablema vesicarium"
    ]
    
    # Collect dataset information
    all_datasets = {}
    total_records = 0
    
    for species_name in species:
        csv_file = data_dir / f"{species_name.replace(' ', '_')}_occurrences.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            total_records += len(df)
            
            # Get unique datasets based on institution code and dataset name
            for _, row in df.iterrows():
                institution = row.get('institutionCode', 'Unknown')
                dataset_name = row.get('datasetName', 'Unknown')
                collection = row.get('collectionCode', 'Unknown')
                
                # Create a unique key
                dataset_key = f"{institution}_{collection}"
                
                if dataset_key not in all_datasets:
                    all_datasets[dataset_key] = {
                        'institutionCode': institution,
                        'datasetName': dataset_name,
                        'collectionCode': collection,
                        'species_count': 1,
                        'record_count': 1
                    }
                else:
                    all_datasets[dataset_key]['species_count'] += 1
                    all_datasets[dataset_key]['record_count'] += 1
    
    # Create citation markdown file
    citation_md = data_dir / "CITATION.md"
    with open(citation_md, 'w') as f:
        f.write("# GBIF Data Citation Information\n\n")
        f.write("## GBIF Citation\n\n")
        f.write("When using this data, please cite GBIF:\n\n")
        f.write("```\n")
        f.write("GBIF.org (2024) GBIF Occurrence Download https://doi.org/10.15468/dl.xxxxx\n")
        f.write("```\n\n")
        f.write("## Data Usage Terms\n\n")
        f.write("This data is subject to the [GBIF Data Use Agreement](https://www.gbif.org/terms).\n\n")
        f.write("## Citation Guidelines\n\n")
        f.write("When using this data, please cite both GBIF and the original data providers as listed below.\n\n")
        f.write("## Species Included\n\n")
        for species_name in species:
            f.write(f"- {species_name}\n")
        f.write("\n## Data Filters Applied\n\n")
        f.write("- Coordinate uncertainty: ≤ 20km\n")
        f.write("- Has coordinates: Yes\n")
        f.write("- No geospatial issues: Yes\n")
        f.write(f"\n## Download Date\n\n{datetime.now().isoformat()}\n")
        f.write(f"\n## Total Records\n\n{total_records} occurrence records\n")
        
        if all_datasets:
            f.write("\n## Data Sources\n\n")
            f.write("The following data sources were used:\n\n")
            for dataset_key, info in all_datasets.items():
                f.write(f"### {info['institutionCode']} - {info['collectionCode']}\n")
                f.write(f"- Dataset: {info['datasetName']}\n")
                f.write(f"- Institution: {info['institutionCode']}\n")
                f.write(f"- Collection: {info['collectionCode']}\n")
                f.write(f"- Records: {info['record_count']}\n\n")
    
    # Create citation JSON file
    citation_json = data_dir / "citation_info.json"
    citation_data = {
        "gbif_citation": "GBIF.org (2024) GBIF Occurrence Download https://doi.org/10.15468/dl.xxxxx",
        "download_date": datetime.now().isoformat(),
        "data_usage_terms": "This data is subject to the GBIF Data Use Agreement: https://www.gbif.org/terms",
        "citation_guidelines": "When using this data, please cite both GBIF and the original data providers as listed in the dataset files.",
        "species_included": species,
        "total_records": total_records,
        "data_filters": {
            "coordinate_uncertainty": "≤ 20km",
            "has_coordinates": True,
            "no_geospatial_issues": True
        },
        "datasets": all_datasets
    }
    
    with open(citation_json, 'w') as f:
        json.dump(citation_data, f, indent=2)
    
    print(f"Citation information saved to:")
    print(f"  - {citation_md}")
    print(f"  - {citation_json}")
    print(f"\nFound {len(all_datasets)} unique data sources")
    print(f"Total records: {total_records}")

if __name__ == "__main__":
    create_citation_files() 