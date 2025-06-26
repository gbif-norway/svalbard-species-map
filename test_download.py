#!/usr/bin/env python3
"""
Test script for GBIF data download pipeline

This script tests the GBIF API connection and species key retrieval
before running the full download pipeline.
"""

import logging
from pathlib import Path
from pygbif import occurrences
from gbif_config import SPECIES, validate_config

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'test_download.log'),
        logging.StreamHandler()
    ]
)

def test_gbif_connection():
    """Test basic GBIF API connection."""
    try:
        # Try a simple search
        result = occurrences.search(q="Calanus", limit=1)
        if result and 'results' in result:
            logging.info("✅ GBIF API connection successful")
            return True
        else:
            logging.error("❌ GBIF API returned unexpected response")
            return False
    except Exception as e:
        logging.error(f"❌ GBIF API connection failed: {e}")
        return False

def test_species_keys():
    """Test species key retrieval for all target species."""
    logging.info("Testing species key retrieval...")
    
    success_count = 0
    for species in SPECIES:
        try:
            result = occurrences.search(q=species, limit=1)
            if result['results']:
                species_key = result['results'][0]['speciesKey']
                logging.info(f"✅ {species}: speciesKey = {species_key}")
                success_count += 1
            else:
                logging.warning(f"⚠️  {species}: No species key found")
        except Exception as e:
            logging.error(f"❌ {species}: Error retrieving species key - {e}")
    
    logging.info(f"Species key test: {success_count}/{len(SPECIES)} successful")
    return success_count == len(SPECIES)

def test_configuration():
    """Test configuration validation."""
    logging.info("Testing configuration...")
    
    if validate_config():
        logging.info("✅ Configuration validation passed")
        return True
    else:
        logging.warning("⚠️  Configuration validation failed - credentials not set")
        logging.info("   This is expected if you haven't set up GBIF credentials yet")
        return False

def main():
    """Run all tests."""
    logging.info("Starting GBIF download pipeline tests")
    
    tests = [
        ("GBIF API Connection", test_gbif_connection),
        ("Species Key Retrieval", test_species_keys),
        ("Configuration Validation", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logging.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                logging.info(f"✅ {test_name} PASSED")
            else:
                logging.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logging.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logging.info(f"\n--- Test Summary ---")
    logging.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logging.info("🎉 All tests passed! Ready to run the download pipeline.")
        return True
    else:
        logging.warning("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 