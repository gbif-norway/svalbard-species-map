FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install GDAL and other geospatial dependencies via conda
RUN conda install -c conda-forge \
    gdal \
    geopandas \
    pandas \
    requests \
    tqdm \
    pygbif \
    -y \
    && conda clean -afy

# Create data and logs directories
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command
CMD ["python", "download_gbif_data.py"] 