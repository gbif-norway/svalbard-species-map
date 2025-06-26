# Svalbard Species Map - GBIF Data Pipeline

This project downloads occurrence data from GBIF for six marine species found in the Svalbard region, with location precision within 20km. The pipeline uses GBIF's download API to generate a unique DOI for the entire dataset.

## Features

- Downloads occurrence data for 6 marine species from GBIF
- Filters data to ensure location precision within 20km
- Uses GBIF download API to generate a unique DOI for the dataset
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
- `logs/gbif_download.log` - Detailed logs

## Data Output

### Files Generated

1. **`all_species_occurrences.csv`** - Main dataset with all occurrence records
2. **`gbif_citation.json`** - Machine-readable citation information including DOI
3. **`CITATION.md`** - Human-readable citation file for academic use
4. **`download_summary.json`** - Summary statistics and metadata

### Data Quality Filters

- Coordinate uncertainty ≤ 20km
- Has valid coordinates
- No geospatial issues
- All six target species

## Citation Information

When using this data, please cite:

1. **GBIF**: The DOI provided in the citation files
2. **Original data providers**: Listed in the dataset files

Example citation:
```
GBIF.org (2024) GBIF Occurrence Download https://doi.org/10.15468/dl.xxxxx
```

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

# Run the download
python download_gbif_data.py

# Run tests
python test_download.py
```

## Configuration

Edit `gbif_config.py` to customize:

- Species list
- Data quality filters
- Download format
- File paths

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your GBIF credentials are correct
2. **Download Timeout**: Large downloads may take up to 1 hour to prepare
3. **No Data Found**: Check if species names are correct in GBIF

### Logs

Check `logs/gbif_download.log` for detailed information about the download process.

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