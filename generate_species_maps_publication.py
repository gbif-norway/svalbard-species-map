#!/usr/bin/env python3
"""
Species Distribution Map Generator for Publication (1/4 width optimized)

This script generates species distribution maps optimized for publication display
at reduced sizes (1/4 width). Enhanced for better readability with:
- Higher DPI for sharp text
- Larger font sizes
- Simplified visual elements
- Better contrast
- Optimized colorbar design
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import geopandas as gpd
from pathlib import Path
import logging
from gbif_config import (
    SPECIES, 
    DATA_DIR, 
    LOGS_DIR, 
    MAPS_DIR,
    SVALBARD_BOUNDS,
    MAP_RESOLUTION_KM,
    MAP_DPI,
    MAP_FORMAT
)

# Publication-optimized settings
PUB_DPI = 600  # Higher DPI for sharp text at small sizes
PUB_FORMAT = 'pdf'  # Vector format for scalability
PUB_FIGSIZE = (8, 6)  # Smaller figure size, better aspect ratio for publications
PUB_MAPS_DIR = MAPS_DIR / "publication"

# Create directories if they don't exist
PUB_MAPS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'species_maps_publication.log'),
        logging.StreamHandler()
    ]
)

def create_grid(bounds, resolution_km):
    """
    Create a regular grid for the specified region.
    
    Args:
        bounds (dict): Dictionary with min_lon, max_lon, min_lat, max_lat
        resolution_km (float): Grid resolution in kilometers
    
    Returns:
        tuple: (lons, lats) arrays of grid cell centers
    """
    # Convert km to approximate degrees (rough approximation)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 * cos(latitude) km
    lat_resolution = resolution_km / 111.0
    lon_resolution = resolution_km / (111.0 * np.cos(np.radians((bounds['min_lat'] + bounds['max_lat']) / 2)))
    
    # Create grid
    lons = np.arange(bounds['min_lon'], bounds['max_lon'] + lon_resolution, lon_resolution)
    lats = np.arange(bounds['min_lat'], bounds['max_lat'] + lat_resolution, lat_resolution)
    
    return lons, lats

def count_occurrences_in_grid(df, lons, lats, species_name):
    """
    Count occurrences in each grid cell for a specific species.
    
    Args:
        df (DataFrame): Occurrence data
        lons (array): Longitude grid centers
        lats (array): Latitude grid centers
        species_name (str): Name of the species
    
    Returns:
        array: 2D array with occurrence counts per grid cell
    """
    # Filter data for the specific species
    species_data = df[df['species'] == species_name].copy()
    
    if len(species_data) == 0:
        logging.warning(f"No data found for species: {species_name}")
        return np.zeros((len(lats), len(lons)))
    
    # Create grid for counting
    grid_counts = np.zeros((len(lats), len(lons)))
    
    # Convert to degrees for grid resolution
    lat_resolution = MAP_RESOLUTION_KM / 111.0
    lon_resolution = MAP_RESOLUTION_KM / (111.0 * np.cos(np.radians((SVALBARD_BOUNDS['min_lat'] + SVALBARD_BOUNDS['max_lat']) / 2)))
    
    # Count occurrences in each grid cell
    for _, row in species_data.iterrows():
        if pd.notna(row['decimalLongitude']) and pd.notna(row['decimalLatitude']):
            lon_idx = int((row['decimalLongitude'] - SVALBARD_BOUNDS['min_lon']) / lon_resolution)
            lat_idx = int((row['decimalLatitude'] - SVALBARD_BOUNDS['min_lat']) / lat_resolution)
            
            # Check if within grid bounds
            if 0 <= lon_idx < len(lons) and 0 <= lat_idx < len(lats):
                grid_counts[lat_idx, lon_idx] += 1
    
    return grid_counts

def create_publication_species_map(species_name, grid_counts, lons, lats, output_path):
    """
    Create a publication-optimized species distribution map.
    
    Args:
        species_name (str): Name of the species
        grid_counts (array): 2D array with occurrence counts
        lons (array): Longitude grid centers
        lats (array): Latitude grid centers
        output_path (Path): Output file path
    """
    # Set up the figure and projection with publication-optimized settings
    plt.rcParams.update({
        'font.size': 14,           # Larger base font size
        'axes.titlesize': 16,      # Larger title
        'axes.labelsize': 12,      # Larger axis labels
        'xtick.labelsize': 10,     # Larger tick labels
        'ytick.labelsize': 10,     # Larger tick labels
        'legend.fontsize': 10,     # Larger legend
        'figure.titlesize': 18,    # Larger figure title
        'font.weight': 'bold',     # Bold fonts for better visibility
        'axes.linewidth': 1.5,     # Thicker axis lines
    })
    
    fig, ax = plt.subplots(
        figsize=PUB_FIGSIZE,
        subplot_kw={'projection': ccrs.LambertConformal(
            central_longitude=20,
            central_latitude=77.5
        )}
    )
    
    # Set map extent
    ax.set_extent([
        SVALBARD_BOUNDS['min_lon'], 
        SVALBARD_BOUNDS['max_lon'],
        SVALBARD_BOUNDS['min_lat'], 
        SVALBARD_BOUNDS['max_lat']
    ], crs=ccrs.PlateCarree())
    
    # Add simplified map features for better readability
    ax.add_feature(cfeature.LAND, alpha=0.8, color='lightgray', edgecolor='black', linewidth=1)
    ax.add_feature(cfeature.OCEAN, alpha=0.4, color='lightblue')
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5, color='black')
    
    # Simplified gridlines - only show major lines
    gl = ax.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False,
                     linewidth=1, color='gray', alpha=0.7, linestyle='--')
    gl.xlabel_style = {'size': 11, 'weight': 'bold'}
    gl.ylabel_style = {'size': 11, 'weight': 'bold'}
    
    # Create meshgrid for plotting
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # High-contrast colormap optimized for small display
    colors = ['#FFF7EC', '#FDD49E', '#FDBB84', '#FC8D59', '#EF6548', '#D7301F', '#B30000', '#7F0000']
    cmap = LinearSegmentedColormap.from_list('pub_cmap', colors, N=256)
    
    # Normalize data for better visualization
    max_count = np.max(grid_counts)
    if max_count > 0:
        # Use square root normalization for better visibility of low counts
        from matplotlib.colors import PowerNorm
        norm = PowerNorm(gamma=0.5, vmin=1, vmax=max_count)
    else:
        norm = plt.Normalize(vmin=0, vmax=1)
    
    # Plot the grid cells with higher alpha for better visibility
    im = ax.pcolormesh(lon_mesh, lat_mesh, grid_counts, 
                      transform=ccrs.PlateCarree(),
                      cmap=cmap, norm=norm, alpha=0.9, rasterized=True)
    
    # Simplified colorbar with fewer ticks for cleaner look
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.08, aspect=15)
    cbar.set_label('Occurrences', fontsize=13, fontweight='bold')
    cbar.ax.tick_params(labelsize=10, width=1.5)
    
    # Simplified colorbar ticks
    if max_count > 0:
        if max_count <= 5:
            tick_positions = np.arange(1, max_count + 1)
        elif max_count <= 20:
            tick_positions = [1, max_count//2, max_count]
        else:
            tick_positions = [1, max_count//4, max_count//2, max_count]
        
        # Apply the same normalization to tick positions
        if max_count > 0:
            cbar.set_ticks(tick_positions)
            cbar.set_ticklabels([str(int(tick)) for tick in tick_positions])
    
    # Shortened title for better fit
    species_short = species_name.split()
    if len(species_short) >= 2:
        title = f"{species_short[0][0]}. {species_short[1]}"
    else:
        title = species_name
    
    plt.title(f'{title}', fontsize=16, fontweight='bold', pad=15)
    
    # Simplified statistics in corner (smaller text box)
    total_occurrences = int(np.sum(grid_counts))
    stats_text = f'n = {total_occurrences}'
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='bottom', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black'))
    
    # Save the map with high DPI and tight layout
    plt.tight_layout()
    plt.savefig(output_path, dpi=PUB_DPI, bbox_inches='tight', format=PUB_FORMAT,
                facecolor='white', edgecolor='none')
    plt.close()
    
    # Reset matplotlib parameters
    plt.rcParams.update(plt.rcParamsDefault)
    
    logging.info(f"Publication map saved: {output_path}")
    logging.info(f"Species: {species_name}, Total occurrences: {total_occurrences}")

def create_publication_combined_map(df, lons, lats):
    """
    Create a publication-optimized combined map showing all species together.
    """
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
        'figure.titlesize': 18,
        'font.weight': 'bold',
        'axes.linewidth': 1.5,
    })
    
    # Count total occurrences (all species) in each grid cell
    grid_counts = np.zeros((len(lats), len(lons)))
    
    lat_resolution = MAP_RESOLUTION_KM / 111.0
    lon_resolution = MAP_RESOLUTION_KM / (111.0 * np.cos(np.radians((SVALBARD_BOUNDS['min_lat'] + SVALBARD_BOUNDS['max_lat']) / 2)))
    
    for _, row in df.iterrows():
        if pd.notna(row['decimalLongitude']) and pd.notna(row['decimalLatitude']):
            lon_idx = int((row['decimalLongitude'] - SVALBARD_BOUNDS['min_lon']) / lon_resolution)
            lat_idx = int((row['decimalLatitude'] - SVALBARD_BOUNDS['min_lat']) / lat_resolution)
            
            if 0 <= lon_idx < len(lons) and 0 <= lat_idx < len(lats):
                grid_counts[lat_idx, lon_idx] += 1
    
    # Create the combined map
    fig, ax = plt.subplots(
        figsize=PUB_FIGSIZE,
        subplot_kw={'projection': ccrs.LambertConformal(
            central_longitude=20,
            central_latitude=77.5
        )}
    )
    
    # Set map extent
    ax.set_extent([
        SVALBARD_BOUNDS['min_lon'], 
        SVALBARD_BOUNDS['max_lon'],
        SVALBARD_BOUNDS['min_lat'], 
        SVALBARD_BOUNDS['max_lat']
    ], crs=ccrs.PlateCarree())
    
    # Add simplified map features
    ax.add_feature(cfeature.LAND, alpha=0.8, color='lightgray', edgecolor='black', linewidth=1)
    ax.add_feature(cfeature.OCEAN, alpha=0.4, color='lightblue')
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5, color='black')
    
    # Simplified gridlines
    gl = ax.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False,
                     linewidth=1, color='gray', alpha=0.7, linestyle='--')
    gl.xlabel_style = {'size': 11, 'weight': 'bold'}
    gl.ylabel_style = {'size': 11, 'weight': 'bold'}
    
    # Create meshgrid for plotting
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # High-contrast colormap
    colors = ['#FFF7EC', '#FDD49E', '#FDBB84', '#FC8D59', '#EF6548', '#D7301F', '#B30000', '#7F0000']
    cmap = LinearSegmentedColormap.from_list('pub_combined_cmap', colors, N=256)
    
    # Normalize data
    max_count = np.max(grid_counts)
    if max_count > 0:
        from matplotlib.colors import PowerNorm
        norm = PowerNorm(gamma=0.5, vmin=1, vmax=max_count)
    else:
        norm = plt.Normalize(vmin=0, vmax=1)
    
    # Plot the grid cells
    im = ax.pcolormesh(lon_mesh, lat_mesh, grid_counts, 
                      transform=ccrs.PlateCarree(),
                      cmap=cmap, norm=norm, alpha=0.9, rasterized=True)
    
    # Simplified colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.08, aspect=15)
    cbar.set_label('Total Occurrences', fontsize=13, fontweight='bold')
    cbar.ax.tick_params(labelsize=10, width=1.5)
    
    # Simplified colorbar ticks
    if max_count > 0:
        if max_count <= 5:
            tick_positions = np.arange(1, max_count + 1)
        elif max_count <= 20:
            tick_positions = [1, max_count//2, max_count]
        else:
            tick_positions = [1, max_count//4, max_count//2, max_count]
        
        cbar.set_ticks(tick_positions)
        cbar.set_ticklabels([str(int(tick)) for tick in tick_positions])
    
    # Simplified title
    plt.title('Combined Species Distribution', fontsize=16, fontweight='bold', pad=15)
    
    # Compact species list
    species_count = len(SPECIES)
    stats_text = f'{species_count} species\nn = {int(np.sum(grid_counts))}'
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='bottom', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black'))
    
    # Save the combined map
    output_path = PUB_MAPS_DIR / f"combined_species_distribution_publication.{PUB_FORMAT}"
    plt.tight_layout()
    plt.savefig(output_path, dpi=PUB_DPI, bbox_inches='tight', format=PUB_FORMAT,
                facecolor='white', edgecolor='none')
    plt.close()
    
    # Reset matplotlib parameters
    plt.rcParams.update(plt.rcParamsDefault)
    
    logging.info(f"Publication combined map saved: {output_path}")

def generate_publication_maps():
    """
    Generate publication-optimized distribution maps for all species.
    """
    # Check if data file exists
    data_file = DATA_DIR / "all_species_occurrences.csv"
    if not data_file.exists():
        logging.error(f"Data file not found: {data_file}")
        logging.error("Please run the download pipeline first: python download_gbif_data.py")
        return False
    
    # Load the data
    logging.info("Loading occurrence data for publication maps...")
    df = pd.read_csv(data_file)
    
    # Filter data to Svalbard region
    svalbard_data = df[
        (df['decimalLongitude'] >= SVALBARD_BOUNDS['min_lon']) &
        (df['decimalLongitude'] <= SVALBARD_BOUNDS['max_lon']) &
        (df['decimalLatitude'] >= SVALBARD_BOUNDS['min_lat']) &
        (df['decimalLatitude'] <= SVALBARD_BOUNDS['max_lat'])
    ].copy()
    
    logging.info(f"Found {len(svalbard_data)} occurrences in Svalbard region")
    
    # Create grid
    lons, lats = create_grid(SVALBARD_BOUNDS, MAP_RESOLUTION_KM)
    logging.info(f"Created grid: {len(lons)} x {len(lats)} cells ({MAP_RESOLUTION_KM}km resolution)")
    
    # Generate publication-optimized maps for each species
    for species in SPECIES:
        logging.info(f"Generating publication map for: {species}")
        
        # Count occurrences in grid
        grid_counts = count_occurrences_in_grid(svalbard_data, lons, lats, species)
        
        # Create output filename
        species_filename = species.replace(' ', '_').lower()
        output_path = PUB_MAPS_DIR / f"{species_filename}_publication.{PUB_FORMAT}"
        
        # Generate the publication map
        create_publication_species_map(species, grid_counts, lons, lats, output_path)
    
    # Create a publication-optimized combined map
    logging.info("Generating publication combined species map...")
    create_publication_combined_map(svalbard_data, lons, lats)
    
    logging.info("All publication-optimized maps generated successfully!")
    logging.info(f"Maps saved in: {PUB_MAPS_DIR}")
    
    # Create a summary file with recommendations
    create_publication_guidelines()
    
    return True

def create_publication_guidelines():
    """
    Create a guidelines file with recommendations for using the maps in publications.
    """
    guidelines_content = """# Publication Map Guidelines

## Optimizations Applied for 1/4 Width Display

### Visual Improvements:
- **Higher DPI (600)**: Ensures sharp text and lines at reduced sizes
- **Vector format (PDF)**: Scalable without quality loss
- **Bold fonts**: Better visibility when scaled down
- **High-contrast colormap**: Improved differentiation of values
- **Simplified gridlines**: Reduced visual clutter
- **Larger font sizes**: 14pt base, 16pt titles for readability

### Design Choices:
- **Compact figure size (8x6)**: Better aspect ratio for publications
- **Shortened species names**: e.g., "C. finmarchicus" instead of full name
- **Simplified statistics**: Only essential information (n = count)
- **Power normalization**: Better visibility of low occurrence values
- **Reduced colorbar ticks**: Cleaner appearance

### Recommended Usage:
1. **For single-column display**: Use individual species maps
2. **For multi-panel figures**: Consider 2x2 or 2x3 grid layouts
3. **Caption recommendations**: Include full species names in figure caption
4. **File format**: Use PDF for vector graphics, PNG if raster needed
5. **Minimum display width**: 2 inches for readability

### Technical Specifications:
- **DPI**: 600 (publication quality)
- **Format**: PDF (vector) or PNG (raster)
- **Color space**: RGB
- **Font**: Default matplotlib font with bold weight
- **Aspect ratio**: 4:3 (width:height)

### Files Generated:
- Individual species maps: `{species}_publication.pdf`
- Combined overview: `combined_species_distribution_publication.pdf`
- High resolution suitable for 1/4 page width display
"""
    
    guidelines_path = PUB_MAPS_DIR / "PUBLICATION_GUIDELINES.md"
    with open(guidelines_path, 'w') as f:
        f.write(guidelines_content)
    
    logging.info(f"Publication guidelines saved: {guidelines_path}")

def main():
    """Main function to generate publication-optimized species distribution maps."""
    logging.info("Starting publication-optimized species distribution map generation...")
    
    success = generate_publication_maps()
    
    if success:
        logging.info("Publication-optimized species distribution maps generated successfully!")
        logging.info(f"Maps saved in: {PUB_MAPS_DIR}")
        logging.info("See PUBLICATION_GUIDELINES.md for usage recommendations")
    else:
        logging.error("Failed to generate publication-optimized species distribution maps")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())