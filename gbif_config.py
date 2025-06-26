#!/usr/bin/env python3
"""
GBIF Configuration File

This file contains configuration settings for GBIF API access.
You need to set up your GBIF account credentials here.
"""

import os
from pathlib import Path

# GBIF Account Configuration
# You need to create a GBIF account at https://www.gbif.org/
# and set your credentials here or as environment variables

GBIF_USERNAME = os.getenv('GBIF_USERNAME', 'your_email@example.com')
GBIF_PASSWORD = os.getenv('GBIF_PASSWORD', 'your_password')

# Download settings
DOWNLOAD_FORMAT = 'SIMPLE_CSV'  # Options: SIMPLE_CSV, DWCA, SIMPLE_JSON
EMAIL_NOTIFICATION = True  # Receive email when download is ready

# Data quality filters
COORDINATE_UNCERTAINTY_MAX = 20000  # 20km in meters
HAS_COORDINATE = True
NO_GEOSPATIAL_ISSUES = True

# Species list
SPECIES = [
    "Calanus finmarchicus",
    "Calanus glacialis", 
    "Parasagitta elegans",
    "Semibalanus balanoides",
    "Oithona similis",
    "Catablema vesicarium"
]

# Map configuration for Svalbard region
SVALBARD_BOUNDS = {
    'min_lon': 10.0,   # Western boundary
    'max_lon': 35.0,   # Eastern boundary
    'min_lat': 74.0,   # Southern boundary
    'max_lat': 81.0    # Northern boundary
}

# Map resolution settings
MAP_RESOLUTION_KM = 20  # 20km x 20km grid cells
MAP_DPI = 300  # High resolution for publication
MAP_FORMAT = 'png'  # Output format

# File paths
DATA_DIR = Path("data")
LOGS_DIR = Path("logs")
MAPS_DIR = Path("data/maps")  # Directory for generated maps

def validate_config():
    """Validate that GBIF credentials are properly configured."""
    if GBIF_USERNAME == 'your_email@example.com' or GBIF_PASSWORD == 'your_password':
        print("⚠️  WARNING: Please configure your GBIF credentials in gbif_config.py")
        print("   or set GBIF_USERNAME and GBIF_PASSWORD environment variables.")
        print("   You can create a GBIF account at https://www.gbif.org/")
        print("   Or run: python setup_credentials.py")
        return False
    return True

def get_download_params(species_keys):
    """Get download parameters for the specified species keys."""
    # Convert species keys to string format for the query
    species_keys_str = [str(key) for key in species_keys]
    
    # Create queries as strings (the format expected by pygbif)
    queries = [
        f'taxonKey in [{",".join(species_keys_str)}]',
        f'coordinateUncertaintyInMeters <= {COORDINATE_UNCERTAINTY_MAX}',
        f'hasCoordinate = {str(HAS_COORDINATE).upper()}',
        f'hasGeospatialIssue = {str(not NO_GEOSPATIAL_ISSUES).upper()}'
    ]
    
    return queries 