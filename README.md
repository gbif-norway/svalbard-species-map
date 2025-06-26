# Svalbard Species Map - GBIF Data Pipeline

This project downloads occurrence data from GBIF for six marine species found in the Svalbard region, with location precision within 20km. The pipeline uses GBIF's download API to generate a unique DOI for the entire dataset and creates species distribution maps for publication.

## Features

- Downloads occurrence data for 6 marine species from GBIF
- Filters data to ensure location precision within 20km
- Uses GBIF download API to generate a unique DOI for the dataset
- Generates high-resolution species distribution maps (20km x 20km resolution)
- Maps focused on Svalbard region with publication-quality output
- Provides proper citation information and data attribution
- Dockerized for easy deployment and reproducibility
- Comprehensive logging and error handling

## Species Included

- Calanus finmarchicus
- Calanus glacialis
- Parasagitta elegans
- Semibalanus balanoides
- Oithona similis
- Catablema vesicarium

## Prerequisites

### GBIF Account Setup

**IMPORTANT**: You need a GBIF account to use the download API and get a DOI.

1. Create a free account at [GBIF.org](https://www.gbif.org/)
2. Go to your account settings to get your credentials
3. Set your credentials in one of these ways:
   - Update `gbif_config.py` with your email and password
   - Set environment variables: `GBIF_USERNAME` and `GBIF_PASSWORD`

### Docker Setup

- Docker and Docker Compose installed
- At least 2GB of available disk space for data storage

## Quick Start

### 1. Configure GBIF Credentials

Edit `gbif_config.py` and update the credentials:

```python
GBIF_USERNAME = 'your_actual_email@example.com'
GBIF_PASSWORD = 'your_actual_password'
```

Or set environment variables:

```bash
export GBIF_USERNAME="your_actual_email@example.com"
export GBIF_PASSWORD="your_actual_password"
```

### 2. Run with Docker

```bash
# Build and run the pipeline
./run_docker.sh

# Or manually:
docker-compose up --build
```

### 3. Check Results

The pipeline will create:
- `data/all_species_occurrences.csv` - Combined dataset with all species
- `data/gbif_citation.json` - Citation information with DOI
- `data/CITATION.md` - Human-readable citation file
- `data/download_summary.json` - Summary of the download
- `data/maps/` - Directory containing species distribution maps
- `logs/gbif_download.log` - Detailed logs

## Data Output

### Files Generated

1. **`all_species_occurrences.csv`** - Main dataset with all occurrence records
2. **`gbif_citation.json`** - Machine-readable citation information including DOI
3. **`CITATION.md`** - Human-readable citation file for academic use
4. **`download_summary.json`** - Summary statistics and metadata
5. **Species Distribution Maps** - High-resolution maps for each species and combined view

### Map Output

The pipeline generates the following maps in `data/maps/`:

- **Individual species maps**: One map per species showing distribution patterns
- **Combined species map**: Overview map showing all species together
- **Map specifications**:
  - Resolution: 20km x 20km grid cells
  - Region: Svalbard and surrounding waters (10°E-35°E, 74°N-81°N)
  - Format: High-resolution PNG (300 DPI)
  - Projection: Lambert Conformal Conic (optimized for Svalbard region)

### Data Quality Filters

- Coordinate uncertainty ≤ 20km
- Has valid coordinates
- No geospatial issues
- All six target species

## Citation Information

When using this data, please cite:

1. **GBIF**: The DOI provided in the citation files
2. **Original data providers**: Listed in the dataset files

**Current Citation:**
```
GBIF.org (26 June 2025) GBIF Occurrence Download https://doi.org/10.15468/dl.dsk2rq
```

**Download Information:**
- **DOI**: [10.15468/dl.dsk2rq](https://doi.org/10.15468/dl.dsk2rq)
- **Download URL**: [https://www.gbif.org/occurrence/download/0069778-250525065834625](https://www.gbif.org/occurrence/download/0069778-250525065834625)
- **Total Records**: 77,536 occurrence records
- **Datasets**: 155 datasets from 74 publishers across 23 countries

## Docker Commands

```bash
# Build the image
docker build -t svalbard-species-downloader .

# Run the download
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs \
  -e GBIF_USERNAME=your_email -e GBIF_PASSWORD=your_password \
  svalbard-species-downloader

# Run with docker-compose
docker-compose up --build

# View logs
docker-compose logs -f

# Clean up
docker-compose down
```

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
# Set credentials
export GBIF_USERNAME="your_email@example.com"
export GBIF_PASSWORD="your_password"

# Run the complete pipeline (download + maps)
python download_gbif_data.py

# Run only map generation (if data already exists)
python generate_species_maps.py

# Run tests
python test_download.py
```

## Configuration

Edit `gbif_config.py` to customize:

- Species list
- Data quality filters
- Download format
- Map settings (resolution, region bounds, output format)
- File paths

### Map Configuration

You can customize the map generation in `gbif_config.py`:

```python
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
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your GBIF credentials are correct
2. **Download Timeout**: Large downloads may take up to 1 hour to prepare
3. **No Data Found**: Check if species names are correct in GBIF
4. **Map Generation Errors**: Ensure all dependencies are installed (matplotlib, cartopy, etc.)

### Logs

Check `logs/gbif_download.log` for detailed information about the download process.
Check `logs/species_maps.log` for map generation details.

## Data Usage Terms

This data is subject to the [GBIF Data Use Agreement](https://www.gbif.org/terms). Please ensure you comply with the terms when using this data.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_download.py`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 