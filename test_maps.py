#!/usr/bin/env python3
"""
Test script for species distribution map generation.

This script creates sample data and tests the map generation functionality.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from gbif_config import DATA_DIR, SPECIES, SVALBARD_BOUNDS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sample_data():
    """Create sample occurrence data for testing."""
    logging.info("Creating sample occurrence data...")
    
    # Create sample data for each species
    sample_data = []
    
    for species in SPECIES:
        # Generate random points within Svalbard region
        n_points = np.random.randint(10, 50)  # Random number of points per species
        
        lons = np.random.uniform(SVALBARD_BOUNDS['min_lon'], SVALBARD_BOUNDS['max_lon'], n_points)
        lats = np.random.uniform(SVALBARD_BOUNDS['min_lat'], SVALBARD_BOUNDS['max_lat'], n_points)
        
        for i in range(n_points):
            sample_data.append({
                'species': species,
                'decimalLongitude': lons[i],
                'decimalLatitude': lats[i],
                'coordinateUncertaintyInMeters': np.random.randint(1000, 20000),
                'year': np.random.randint(2000, 2024),
                'month': np.random.randint(1, 13),
                'day': np.random.randint(1, 29),
                'basisOfRecord': 'HumanObservation',
                'institutionCode': 'TEST',
                'collectionCode': 'TEST',
                'catalogNumber': f'TEST-{species.replace(" ", "")}-{i:04d}'
            })
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to file
    output_file = DATA_DIR / "all_species_occurrences.csv"
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(output_file, index=False)
    
    logging.info(f"Sample data created with {len(df)} records")
    logging.info(f"Sample data saved to: {output_file}")
    
    return output_file

def test_map_generation():
    """Test the map generation functionality."""
    logging.info("Testing map generation...")
    
    try:
        from generate_species_maps import generate_all_species_maps
        
        # Create sample data if it doesn't exist
        data_file = DATA_DIR / "all_species_occurrences.csv"
        if not data_file.exists():
            create_sample_data()
        
        # Test map generation
        success = generate_all_species_maps()
        
        if success:
            logging.info("✅ Map generation test passed!")
            
            # Check if maps were created
            maps_dir = DATA_DIR / "maps"
            if maps_dir.exists():
                map_files = list(maps_dir.glob("*.png"))
                logging.info(f"Generated {len(map_files)} map files:")
                for map_file in map_files:
                    logging.info(f"  - {map_file.name}")
            else:
                logging.warning("Maps directory not found")
        else:
            logging.error("❌ Map generation test failed!")
            return False
            
    except ImportError as e:
        logging.error(f"❌ Could not import map generation module: {e}")
        logging.error("Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        logging.error(f"❌ Error during map generation test: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    logging.info("Starting species distribution map tests...")
    
    success = test_map_generation()
    
    if success:
        logging.info("🎉 All tests passed! Species distribution maps are working correctly.")
        return 0
    else:
        logging.error("💥 Tests failed! Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit(main()) 