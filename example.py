#!/usr/bin/env python3
"""
Example script showing how to use the Landsat query tool.
"""

from landsat_query import LandsatSceneQuery
import os

def example_query_without_credentials():
    """Example: Query scenes without downloading (no credentials needed)."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Query scenes without credentials")
    print("="*80 + "\n")
    
    query = LandsatSceneQuery()
    
    try:
        # San Francisco Bay Area bounding box
        bbox = (-122.5, 37.5, -122.0, 38.0)
        
        scenes = query.query_scenes(
            bbox=bbox,
            start_date="2023-06-01",
            end_date="2023-08-31",
            max_cloud_cover=30
        )
        
        query.print_scene_summary(scenes)
        
    finally:
        query.disconnect()


def example_query_with_download():
    """Example: Query and download preview images (requires credentials)."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Query and download preview images")
    print("="*80 + "\n")
    
    # Get credentials from environment
    username = os.environ.get('EARTHEXPLORER_USERNAME')
    password = os.environ.get('EARTHEXPLORER_PASSWORD')
    
    if not username or not password:
        print("Skipping: Set EARTHEXPLORER_USERNAME and EARTHEXPLORER_PASSWORD to run this example")
        return
    
    query = LandsatSceneQuery(username, password)
    
    try:
        # Colorado Rocky Mountains
        bbox = (-106.0, 39.5, -105.5, 40.0)
        
        scenes = query.query_scenes(
            bbox=bbox,
            start_date="2023-01-01",
            end_date="2023-03-31",
            max_cloud_cover=20
        )
        
        query.print_scene_summary(scenes)
        
        # Download previews
        query.download_scenes(
            scenes,
            output_dir="./example_previews",
            download_previews=True
        )
        
        # Save metadata
        query.save_scene_list(scenes, "./example_scenes.json")
        
    finally:
        query.disconnect()


def example_different_datasets():
    """Example: Query different Landsat datasets."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Query different Landsat datasets")
    print("="*80 + "\n")
    
    query = LandsatSceneQuery()
    
    try:
        # Yosemite National Park
        bbox = (-119.8, 37.7, -119.3, 38.2)
        
        # Landsat 8-9
        print("\nQuerying Landsat 8-9 (OLI/TIRS)...")
        scenes_l89 = query.query_scenes(
            bbox=bbox,
            start_date="2023-07-01",
            end_date="2023-07-31",
            dataset="landsat_ot_c2_l2",
            max_cloud_cover=10
        )
        print(f"Found {len(scenes_l89)} Landsat 8-9 scenes")
        
        # Landsat 7
        print("\nQuerying Landsat 7 (ETM+)...")
        scenes_l7 = query.query_scenes(
            bbox=bbox,
            start_date="2023-07-01",
            end_date="2023-07-31",
            dataset="landsat_etm_c2_l2",
            max_cloud_cover=10
        )
        print(f"Found {len(scenes_l7)} Landsat 7 scenes")
        
        # Show all scenes
        all_scenes = scenes_l89 + scenes_l7
        query.print_scene_summary(all_scenes)
        
    finally:
        query.disconnect()


if __name__ == '__main__':
    print("\n" + "="*80)
    print("LANDSAT QUERY TOOL - EXAMPLES")
    print("="*80)
    
    # Run examples
    example_query_without_credentials()
    example_query_with_download()
    example_different_datasets()
    
    print("\n" + "="*80)
    print("Examples complete!")
    print("="*80 + "\n")
