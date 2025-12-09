"""
Example usage of snowio for processing Landsat scenes.
"""

from snowio import process_scene, identify_landsat_version
from shapely.geometry import box
import os


def example_single_scene():
    """Example: Process a single Landsat scene."""
    
    # Define paths
    scene_path = "data/LC08_L1TP_043034_20201215_20201226_01_T1"
    output_dir = "output/single_scene"
    
    # Define Area of Interest (bounding box)
    # Example: Sierra Nevada region
    aoi = box(-120.5, 38.5, -120.0, 39.0)
    
    # Process the scene
    print("Processing Landsat scene...")
    output_path = process_scene(
        scene_path=scene_path,
        output_dir=output_dir,
        aoi_geometry=aoi,
        ndsi_threshold=0.4
    )
    
    print(f"Output saved to: {output_path}")


def example_with_glacier_mask():
    """Example: Process scene with glacier mask."""
    
    import numpy as np
    
    scene_path = "data/LC08_L1TP_043034_20201215_20201226_01_T1"
    output_dir = "output/with_glacier"
    
    # Define AOI
    aoi = box(-120.5, 38.5, -120.0, 39.0)
    
    # Create a dummy glacier mask (in real use, load from file)
    # glacier_mask = np.zeros((1000, 1000), dtype=bool)
    # glacier_mask[400:600, 400:600] = True  # Mark center region as glacier
    
    # Process scene
    output_path = process_scene(
        scene_path=scene_path,
        output_dir=output_dir,
        aoi_geometry=aoi,
        glacier_mask=None,  # Pass actual mask here
        ndsi_threshold=0.4
    )
    
    print(f"Output saved to: {output_path}")


def example_identify_version():
    """Example: Identify Landsat version from scene name."""
    
    scenes = [
        "LC08_L1TP_043034_20201215_20201226_01_T1",
        "LC09_L1TP_043034_20211215_20211226_01_T1",
        "LE07_L1TP_043034_20101215_20101226_01_T1",
        "LT05_L1TP_043034_20001215_20001226_01_T1",
    ]
    
    for scene in scenes:
        version = identify_landsat_version(scene)
        print(f"{scene[:4]} -> Landsat {version}")


def example_batch_processing():
    """Example: Process multiple scenes."""
    
    import glob
    
    scenes_dir = "data/landsat_scenes"
    output_dir = "output/batch"
    
    # Find all scene directories
    scene_paths = glob.glob(os.path.join(scenes_dir, "LC*"))
    
    # Define AOI
    aoi = box(-120.5, 38.5, -120.0, 39.0)
    
    # Process each scene
    for scene_path in scene_paths:
        print(f"\nProcessing: {os.path.basename(scene_path)}")
        try:
            output_path = process_scene(
                scene_path=scene_path,
                output_dir=output_dir,
                aoi_geometry=aoi,
                ndsi_threshold=0.4
            )
            print(f"✓ Success: {output_path}")
        except Exception as e:
            print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("snowio Examples")
    print("=" * 60)
    
    # Run examples (uncomment as needed)
    # example_single_scene()
    # example_with_glacier_mask()
    example_identify_version()
    # example_batch_processing()
