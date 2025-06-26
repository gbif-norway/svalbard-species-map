#!/usr/bin/env python3
"""
Update Citation Information Script

This script updates the citation files with the current DOI and download information
from the successful GBIF download.
"""

import json
from pathlib import Path
from gbif_config import DATA_DIR

def update_citation_files():
    """Update citation files with current DOI and download information."""
    
    # Current download information
    download_info = {
        "downloadKey": "0069778-250525065834625",
        "status": "SUCCEEDED",
        "created": "2025-06-26",
        "totalRecords": 77536,
        "format": "SIMPLE_CSV",
        "doi": "10.15468/dl.dsk2rq",
        "downloadUrl": "https://www.gbif.org/occurrence/download/0069778-250525065834625",
        "citation": "GBIF.org (26 June 2025) GBIF Occurrence Download https://doi.org/10.15468/dl.dsk2rq"
    }
    
    # Update JSON citation file
    citation_json = DATA_DIR / "gbif_citation.json"
    with open(citation_json, 'w') as f:
        json.dump(download_info, f, indent=2)
    
    print(f"Updated citation JSON: {citation_json}")
    
    # Update markdown citation file
    citation_md = DATA_DIR / "CITATION.md"
    md_content = f"""# GBIF Data Citation Information

## GBIF Citation

When using this data, please cite GBIF:

```
{download_info['citation']}
```

## Download Information

- **DOI**: [{download_info['doi']}](https://doi.org/{download_info['doi']})
- **Download URL**: [{download_info['downloadUrl']}]({download_info['downloadUrl']})
- **Download Key**: {download_info['downloadKey']}
- **Total Records**: {download_info['totalRecords']:,} occurrence records
- **Download Date**: {download_info['created']}

## Data Usage Terms

This data is subject to the [GBIF Data Use Agreement](https://www.gbif.org/terms).

## Citation Guidelines

When using this data, please cite both GBIF and the original data providers.

## Species Included

- Calanus finmarchicus
- Calanus glacialis
- Parasagitta elegans
- Semibalanus balanoides
- Oithona similis
- Catablema vesicarium

## Data Quality Filters Applied

- Coordinate uncertainty ≤ 20km
- Has valid coordinates
- No geospatial issues
- All six target species

## Involved Datasets

This download includes data from 155 datasets and 74 publishers across 23 countries, including major marine datasets such as:

- Southern Ocean Continuous Zooplankton Recorder (SO-CPR) Survey
- Marine Nature Conservation Review (MNCR)
- IMOS - Zooplankton Abundance and Biomass Index (CPR)
- Norwegian Biodiversity Information Centre datasets
- And many more...

For a complete list of datasets and publishers, visit the [download page]({download_info['downloadUrl']}).
"""
    
    with open(citation_md, 'w') as f:
        f.write(md_content)
    
    print(f"Updated citation markdown: {citation_md}")
    print(f"\nCitation information updated successfully!")
    print(f"DOI: {download_info['doi']}")
    print(f"Download URL: {download_info['downloadUrl']}")

if __name__ == "__main__":
    update_citation_files() 