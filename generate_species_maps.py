#!/usr/bin/env python3
"""
Species Distribution Map Generator for Svalbard Region

This script generates species distribution maps for marine species in the Svalbard region
using occurrence data from GBIF. Maps are created with 20km x 20km resolution grid cells.
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

# Create directories if they don't exist
MAPS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'species_maps.log'),
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

def create_species_map(species_name, grid_counts, lons, lats, output_path):
    """
    Create a species distribution map.
    
    Args:
        species_name (str): Name of the species
        grid_counts (array): 2D array with occurrence counts
        lons (array): Longitude grid centers
        lats (array): Latitude grid centers
        output_path (Path): Output file path
    """
    # Set up the figure and projection
    fig, ax = plt.subplots(
        figsize=(12, 10),
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
    
    # Add map features
    ax.add_feature(cfeature.LAND, alpha=0.7)
    ax.add_feature(cfeature.OCEAN, alpha=0.3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color='gray')
    
    # Add gridlines
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                linewidth=0.5, color='gray', alpha=0.5)
    
    # Create meshgrid for plotting
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # Mask zero counts for better visualization
    masked_counts = np.ma.masked_where(grid_counts == 0, grid_counts)
    
    # Define discrete bins for the colorbar
    # We want a log-like progression since counts vary significantly
    max_count = np.max(grid_counts)
    if max_count <= 0:
        max_count = 1
        
    if max_count <= 5:
        boundaries = [1, 2, 3, 4, 5, 6]
    elif max_count <= 20:
        boundaries = [1, 2, 5, 10, 20, 21]
    else:
        # Custom log-like bins
        boundaries = [1, 2, 5, 10, 50, 100, 500, 1000, 5000, 10000]
        boundaries = [b for b in boundaries if b <= max_count]
        if max_count > boundaries[-1]:
            boundaries.append(max_count + 1)
        else:
            boundaries[-1] = max_count + 1

    # Use a high-contrast colormap with discrete steps
    from matplotlib.colors import BoundaryNorm
    cmap = plt.get_cmap('viridis', len(boundaries)-1)
    norm = BoundaryNorm(boundaries, cmap.N)
    
    # Plot the grid cells
    im = ax.pcolormesh(lon_mesh, lat_mesh, masked_counts, 
                      transform=ccrs.PlateCarree(),
                      cmap=cmap, norm=norm, alpha=0.85, 
                      edgecolor='white', linewidth=0.1)
    
    # Add colorbar with actual numbers
    cbar = plt.colorbar(im, ax=ax, shrink=0.7, pad=0.03, extend='max' if max_count >= boundaries[-1] else 'neither')
    cbar.set_label('Number of Occurrences', fontsize=12, fontweight='bold')
    
    # Set the ticks to the boundaries for clarity
    tick_locs = boundaries[:-1]
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels([str(int(b)) for b in tick_locs])
    
    # Add title
    plt.title(f'Distribution of {species_name}\nSvalbard Region ({MAP_RESOLUTION_KM}km resolution)', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add text with statistics
    total_occurrences = np.sum(grid_counts)
    occupied_cells = np.sum(grid_counts > 0)
    total_cells = len(lons) * len(lats)
    
    stats_text = f'Total occurrences: {total_occurrences}\nOccupied cells: {occupied_cells}/{total_cells}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save the map
    plt.tight_layout()
    plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight', format=MAP_FORMAT)
    plt.close()
    
    logging.info(f"Map saved: {output_path}")
    logging.info(f"Species: {species_name}, Total occurrences: {total_occurrences}, Occupied cells: {occupied_cells}")

def generate_all_species_maps():
    """
    Generate distribution maps for all species.
    """
    # Check if data file exists
    data_file = DATA_DIR / "all_species_occurrences.csv"
    if not data_file.exists():
        logging.error(f"Data file not found: {data_file}")
        logging.error("Please run the download pipeline first: python download_gbif_data.py")
        return False
    
    # Load the data
    logging.info("Loading occurrence data...")
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
    
    # Generate maps for each species
    for species in SPECIES:
        logging.info(f"Generating map for: {species}")
        
        # Count occurrences in grid
        grid_counts = count_occurrences_in_grid(svalbard_data, lons, lats, species)
        
        # Create output filename
        species_filename = species.replace(' ', '_').lower()
        output_path = MAPS_DIR / f"{species_filename}_distribution_map.{MAP_FORMAT}"
        
        # Generate the map
        create_species_map(species, grid_counts, lons, lats, output_path)
    
    # Create a summary map with all species
    logging.info("Generating combined species map...")
    create_combined_map(svalbard_data, lons, lats)
    
    logging.info("All maps generated successfully!")
    return True

def create_combined_map(df, lons, lats):
    """
    Create a combined map showing all species together.
    """
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
        figsize=(12, 10),
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
    
    # Add map features
    ax.add_feature(cfeature.LAND, alpha=0.7)
    ax.add_feature(cfeature.OCEAN, alpha=0.3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color='gray')
    
    # Add gridlines
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                linewidth=0.5, color='gray', alpha=0.5)
    
    # Create meshgrid for plotting
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # Mask zero counts for better visualization
    masked_counts = np.ma.masked_where(grid_counts == 0, grid_counts)
    
    # Define discrete bins for the colorbar
    max_count = np.max(grid_counts)
    if max_count <= 0:
        max_count = 1
        
    if max_count <= 10:
        boundaries = [1, 2, 5, 10, 11]
    else:
        boundaries = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
        boundaries = [b for b in boundaries if b <= max_count]
        if max_count > boundaries[-1]:
            boundaries.append(max_count + 1)
        else:
            boundaries[-1] = max_count + 1

    # Use a high-contrast colormap with discrete steps
    from matplotlib.colors import BoundaryNorm
    cmap = plt.get_cmap('plasma', len(boundaries)-1)
    norm = BoundaryNorm(boundaries, cmap.N)
    
    # Plot the grid cells
    im = ax.pcolormesh(lon_mesh, lat_mesh, masked_counts, 
                      transform=ccrs.PlateCarree(),
                      cmap=cmap, norm=norm, alpha=0.85,
                      edgecolor='white', linewidth=0.1)
    
    # Add colorbar with actual numbers
    cbar = plt.colorbar(im, ax=ax, shrink=0.7, pad=0.03, extend='max' if max_count >= boundaries[-1] else 'neither')
    cbar.set_label('Total Occurrences (All Species)', fontsize=12, fontweight='bold')
    
    # Set the ticks to the boundaries for clarity
    tick_locs = boundaries[:-1]
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels([str(int(b)) for b in tick_locs])
    
    # Add title
    plt.title(f'Combined Species Distribution\nSvalbard Region ({MAP_RESOLUTION_KM}km resolution)', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add species list
    species_list = '\n'.join([f'• {species}' for species in SPECIES])
    ax.text(0.02, 0.98, f'Species included:\n{species_list}', 
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save the combined map
    output_path = MAPS_DIR / f"combined_species_distribution_map.{MAP_FORMAT}"
    plt.tight_layout()
    plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight', format=MAP_FORMAT)
    plt.close()
    
    logging.info(f"Combined map saved: {output_path}")

def main():
    """Main function to generate species distribution maps."""
    logging.info("Starting species distribution map generation...")
    
    success = generate_all_species_maps()
    
    if success:
        logging.info("Species distribution maps generated successfully!")
        logging.info(f"Maps saved in: {MAPS_DIR}")
    else:
        logging.error("Failed to generate species distribution maps")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 