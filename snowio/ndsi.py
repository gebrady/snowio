"""
NDSI (Normalized Difference Snow Index) calculation for Landsat imagery.

NDSI = (G - SWIR1) / (G + SWIR1)
- Landsat 4-7: NDSI = (Band 2 - Band 5) / (Band 2 + Band 5)
- Landsat 8-9: NDSI = (Band 3 - Band 6) / (Band 3 + Band 6)
"""

import os
from typing import Tuple, Optional, Dict
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import mapping


def identify_landsat_version(scene_path: str) -> int:
    """
    Identify Landsat version from scene path or metadata.
    
    Args:
        scene_path: Path to Landsat scene directory or file
        
    Returns:
        Landsat version number (4, 5, 7, 8, or 9)
    """
    scene_name = os.path.basename(scene_path).upper()
    
    # Landsat scene naming convention: LC08_... or LE07_...
    if 'LC08' in scene_name or 'LO08' in scene_name:
        return 8
    elif 'LC09' in scene_name or 'LO09' in scene_name:
        return 9
    elif 'LE07' in scene_name or 'LT07' in scene_name:
        return 7
    elif 'LT05' in scene_name or 'LM05' in scene_name:
        return 5
    elif 'LT04' in scene_name or 'LM04' in scene_name:
        return 4
    
    # Try to infer from metadata file if present
    mtl_file = None
    if os.path.isdir(scene_path):
        for f in os.listdir(scene_path):
            if f.endswith('MTL.txt') or f.endswith('MTL.TXT'):
                mtl_file = os.path.join(scene_path, f)
                break
    
    if mtl_file and os.path.exists(mtl_file):
        with open(mtl_file, 'r') as f:
            content = f.read()
            if 'SPACECRAFT_ID = "LANDSAT_8"' in content:
                return 8
            elif 'SPACECRAFT_ID = "LANDSAT_9"' in content:
                return 9
            elif 'SPACECRAFT_ID = "LANDSAT_7"' in content:
                return 7
            elif 'SPACECRAFT_ID = "LANDSAT_5"' in content:
                return 5
            elif 'SPACECRAFT_ID = "LANDSAT_4"' in content:
                return 4
    
    raise ValueError(f"Could not determine Landsat version from scene: {scene_path}")


def get_band_numbers(landsat_version: int) -> Tuple[int, int]:
    """
    Get the green and SWIR1 band numbers for NDSI calculation.
    
    Args:
        landsat_version: Landsat version (4-9)
        
    Returns:
        Tuple of (green_band, swir1_band) numbers
    """
    if landsat_version in [4, 5, 7]:
        return (2, 5)  # Band 2 (Green), Band 5 (SWIR1)
    elif landsat_version in [8, 9]:
        return (3, 6)  # Band 3 (Green), Band 6 (SWIR1)
    else:
        raise ValueError(f"Unsupported Landsat version: {landsat_version}")


def calculate_ndsi(green_band: np.ndarray, swir1_band: np.ndarray) -> np.ndarray:
    """
    Calculate NDSI from green and SWIR1 bands.
    
    NDSI = (Green - SWIR1) / (Green + SWIR1)
    
    Args:
        green_band: Green band array
        swir1_band: SWIR1 band array
        
    Returns:
        NDSI array with values between -1 and 1
    """
    # Convert to float to avoid integer division issues
    green = green_band.astype(np.float32)
    swir1 = swir1_band.astype(np.float32)
    
    # Calculate denominator
    denominator = green + swir1
    
    # Avoid division by zero
    ndsi = np.zeros_like(green, dtype=np.float32)
    valid_mask = denominator != 0
    
    ndsi[valid_mask] = (green[valid_mask] - swir1[valid_mask]) / denominator[valid_mask]
    
    # Set invalid pixels to NaN
    ndsi[~valid_mask] = np.nan
    
    return ndsi


def load_band(scene_path: str, band_number: int) -> Tuple[np.ndarray, rasterio.profiles.Profile]:
    """
    Load a specific band from a Landsat scene.
    
    Args:
        scene_path: Path to Landsat scene directory or band file
        band_number: Band number to load
        
    Returns:
        Tuple of (band_array, rasterio_profile)
    """
    band_file = None
    
    if os.path.isdir(scene_path):
        # Find the band file in the directory
        for f in os.listdir(scene_path):
            if f.endswith(f'_B{band_number}.TIF') or f.endswith(f'_B{band_number}.tif'):
                band_file = os.path.join(scene_path, f)
                break
    elif os.path.isfile(scene_path):
        # Assume scene_path is the band file itself
        band_file = scene_path
    
    if not band_file or not os.path.exists(band_file):
        raise FileNotFoundError(f"Band {band_number} file not found in {scene_path}")
    
    with rasterio.open(band_file) as src:
        band_data = src.read(1)
        profile = src.profile.copy()
    
    return band_data, profile


def process_scene(
    scene_path: str,
    output_dir: str,
    aoi_geometry: Optional[object] = None,
    glacier_mask: Optional[np.ndarray] = None,
    ndsi_threshold: float = 0.4
) -> str:
    """
    Process a Landsat scene to generate NDSI and snow/glacier classification.
    
    Args:
        scene_path: Path to Landsat scene directory
        output_dir: Output directory for processed layers
        aoi_geometry: Optional shapely geometry for AOI cropping
        glacier_mask: Optional binary mask indicating glacier locations
        ndsi_threshold: NDSI threshold for snow classification (default: 0.4)
        
    Returns:
        Path to output NDSI file
    """
    # Identify Landsat version
    landsat_version = identify_landsat_version(scene_path)
    print(f"Processing Landsat {landsat_version} scene: {scene_path}")
    
    # Get band numbers for NDSI calculation
    green_band_num, swir1_band_num = get_band_numbers(landsat_version)
    
    # Load bands
    print(f"Loading Band {green_band_num} (Green) and Band {swir1_band_num} (SWIR1)")
    green_data, profile = load_band(scene_path, green_band_num)
    swir1_data, _ = load_band(scene_path, swir1_band_num)
    
    # Calculate NDSI
    print("Calculating NDSI...")
    ndsi = calculate_ndsi(green_data, swir1_data)
    
    # Crop to AOI if provided
    if aoi_geometry is not None:
        print("Cropping to AOI...")
        ndsi, profile = crop_to_aoi(ndsi, profile, aoi_geometry)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    scene_name = os.path.basename(scene_path.rstrip('/'))
    ndsi_output = os.path.join(output_dir, f"{scene_name}_NDSI.tif")
    
    # Update profile for output
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw',
        nodata=np.nan
    )
    
    # Write NDSI to file
    print(f"Writing NDSI to {ndsi_output}")
    with rasterio.open(ndsi_output, 'w', **profile) as dst:
        dst.write(ndsi, 1)
    
    # Generate classification (0: unclassified, 1: snow, 2: glacier)
    classification = classify_snow_glacier(ndsi, glacier_mask, ndsi_threshold)
    
    # Write classification to file
    classification_output = os.path.join(output_dir, f"{scene_name}_classification.tif")
    profile.update(dtype=rasterio.uint8, nodata=0)
    
    print(f"Writing classification to {classification_output}")
    with rasterio.open(classification_output, 'w', **profile) as dst:
        dst.write(classification, 1)
    
    return ndsi_output


def crop_to_aoi(
    data: np.ndarray,
    profile: rasterio.profiles.Profile,
    aoi_geometry: object
) -> Tuple[np.ndarray, rasterio.profiles.Profile]:
    """
    Crop raster data to Area of Interest (AOI) geometry.
    
    Args:
        data: Raster data array
        profile: Rasterio profile with spatial reference
        aoi_geometry: Shapely geometry defining the AOI
        
    Returns:
        Tuple of (cropped_data, updated_profile)
    """
    # Create a temporary in-memory raster to use rasterio.mask
    from rasterio.io import MemoryFile
    
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset:
            dataset.write(data, 1)
            
            # Mask the raster with the AOI geometry
            out_image, out_transform = mask(
                dataset,
                [mapping(aoi_geometry)],
                crop=True,
                filled=True
            )
            
            # Update profile
            out_profile = profile.copy()
            out_profile.update({
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
    
    return out_image[0], out_profile


def classify_snow_glacier(
    ndsi: np.ndarray,
    glacier_mask: Optional[np.ndarray] = None,
    ndsi_threshold: float = 0.4
) -> np.ndarray:
    """
    Classify pixels into snow, glacier, or unclassified.
    
    Classification:
    - 0: Unclassified (NDSI below threshold or invalid)
    - 1: Snow (NDSI above threshold, not in glacier area)
    - 2: Glacier (NDSI above threshold, in glaciated area)
    
    Args:
        ndsi: NDSI array
        glacier_mask: Optional binary mask where True/1 indicates glacier
        ndsi_threshold: NDSI threshold for snow/glacier classification
        
    Returns:
        Classification array with values 0, 1, or 2
    """
    classification = np.zeros(ndsi.shape, dtype=np.uint8)
    
    # Identify snow (NDSI >= threshold)
    snow_mask = (ndsi >= ndsi_threshold) & (~np.isnan(ndsi))
    
    # All snow pixels start as class 1
    classification[snow_mask] = 1
    
    # If glacier mask provided, upgrade snow pixels in glacier areas to class 2
    if glacier_mask is not None:
        glacier_snow_mask = snow_mask & (glacier_mask.astype(bool))
        classification[glacier_snow_mask] = 2
    
    return classification
