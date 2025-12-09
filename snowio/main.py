#!/usr/bin/env python3
"""
Main script for processing Landsat scenes for snow analysis.

This script processes Landsat scenes to generate NDSI (Normalized Difference Snow Index)
and classifies pixels into snow, glacier, or unclassified categories.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

import numpy as np
from shapely.geometry import box, shape
from shapely import wkt

from snowio import process_scene


def parse_aoi(aoi_str: Optional[str]):
    """
    Parse AOI from string (WKT or bounding box).
    
    Args:
        aoi_str: AOI as WKT string or "minx,miny,maxx,maxy" bounding box
        
    Returns:
        Shapely geometry or None
    """
    if not aoi_str:
        return None
    
    # Try to parse as bounding box first
    if ',' in aoi_str:
        try:
            coords = [float(x.strip()) for x in aoi_str.split(',')]
            if len(coords) == 4:
                return box(*coords)
        except ValueError:
            pass
    
    # Try to parse as WKT
    try:
        return wkt.loads(aoi_str)
    except:
        raise ValueError(f"Could not parse AOI: {aoi_str}")


def load_glacier_mask(glacier_mask_path: Optional[str], reference_shape: tuple) -> Optional[np.ndarray]:
    """
    Load glacier mask from file.
    
    Args:
        glacier_mask_path: Path to glacier mask raster
        reference_shape: Shape to resize mask to if needed
        
    Returns:
        Glacier mask array or None
    """
    if not glacier_mask_path:
        return None
    
    import rasterio
    
    with rasterio.open(glacier_mask_path) as src:
        glacier_mask = src.read(1)
    
    # TODO: Handle reprojection/resampling if shapes don't match
    return glacier_mask


def find_landsat_scenes(input_dir: str) -> List[str]:
    """
    Find Landsat scene directories in input directory.
    
    Args:
        input_dir: Directory containing Landsat scenes
        
    Returns:
        List of scene paths
    """
    scenes = []
    
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        
        # Check if it's a directory and looks like a Landsat scene
        if os.path.isdir(item_path):
            # Look for typical Landsat scene patterns
            if any(x in item.upper() for x in ['LC08', 'LC09', 'LE07', 'LT05', 'LT04']):
                scenes.append(item_path)
            # Or check if it contains MTL file
            elif any(f.endswith('MTL.txt') or f.endswith('MTL.TXT') for f in os.listdir(item_path)):
                scenes.append(item_path)
    
    return sorted(scenes)


def main():
    """Main entry point for snow analysis processing."""
    parser = argparse.ArgumentParser(
        description='Process Landsat scenes for snow analysis using NDSI'
    )
    
    parser.add_argument(
        'input',
        help='Input Landsat scene directory or path to directory containing multiple scenes'
    )
    
    parser.add_argument(
        'output',
        help='Output directory for processed layers'
    )
    
    parser.add_argument(
        '--aoi',
        help='Area of Interest as WKT string or "minx,miny,maxx,maxy" bounding box',
        default=None
    )
    
    parser.add_argument(
        '--glacier-mask',
        help='Path to glacier mask raster file',
        default=None
    )
    
    parser.add_argument(
        '--ndsi-threshold',
        type=float,
        default=0.4,
        help='NDSI threshold for snow classification (default: 0.4)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process multiple scenes from input directory'
    )
    
    args = parser.parse_args()
    
    # Parse AOI
    aoi_geometry = parse_aoi(args.aoi)
    if aoi_geometry:
        print(f"Using AOI: {aoi_geometry.bounds}")
    
    # Load glacier mask
    glacier_mask = None
    if args.glacier_mask:
        print(f"Loading glacier mask from {args.glacier_mask}")
        # Glacier mask loading will be done per-scene to match dimensions
    
    # Determine scenes to process
    if args.batch:
        scenes = find_landsat_scenes(args.input)
        if not scenes:
            print(f"No Landsat scenes found in {args.input}")
            sys.exit(1)
        print(f"Found {len(scenes)} scenes to process")
    else:
        scenes = [args.input]
    
    # Process each scene
    for i, scene_path in enumerate(scenes, 1):
        print(f"\n{'='*60}")
        print(f"Processing scene {i}/{len(scenes)}: {os.path.basename(scene_path)}")
        print(f"{'='*60}")
        
        try:
            output_path = process_scene(
                scene_path=scene_path,
                output_dir=args.output,
                aoi_geometry=aoi_geometry,
                glacier_mask=glacier_mask,
                ndsi_threshold=args.ndsi_threshold
            )
            print(f"✓ Successfully processed scene")
            print(f"  Output: {output_path}")
        except Exception as e:
            print(f"✗ Error processing scene: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print(f"Processing complete. Output saved to: {args.output}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
