#!/usr/bin/env python3
"""
Landsat Scene Query Tool
Query Landsat scenes using a bounding box AOI and date range.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse

try:
    from landsatxplore.api import API
    from landsatxplore.earthexplorer import EarthExplorer
except ImportError:
    API = None
    EarthExplorer = None
    print("Warning: landsatxplore not installed. Install with: pip install landsatxplore")


class LandsatSceneQuery:
    """
    Query and download Landsat scenes based on bounding box and date range.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Landsat scene query tool.
        
        Args:
            username: USGS EarthExplorer username
            password: USGS EarthExplorer password
        """
        self.username = username
        self.password = password
        self.api = None
        self.ee = None
        
    def connect(self):
        """Connect to the Landsat API."""
        if API is None:
            raise ImportError("landsatxplore is required. Install with: pip install landsatxplore")
        
        if not self.username or not self.password:
            raise ValueError("USGS EarthExplorer credentials required")
            
        self.api = API(self.username, self.password)
        self.ee = EarthExplorer(self.username, self.password)
        
    def disconnect(self):
        """Disconnect from the Landsat API."""
        if self.api:
            self.api.logout()
        if self.ee:
            self.ee.logout()
    
    def query_scenes(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        dataset: str = "landsat_ot_c2_l2",
        max_cloud_cover: int = 100
    ) -> List[Dict]:
        """
        Query Landsat scenes within bounding box and date range.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            dataset: Landsat dataset identifier
            max_cloud_cover: Maximum cloud cover percentage (0-100)
            
        Returns:
            List of scene metadata dictionaries
        """
        if not self.api:
            self.connect()
        
        # Query scenes
        scenes = self.api.search(
            dataset=dataset,
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=max_cloud_cover
        )
        
        # Enhance scene metadata
        enhanced_scenes = []
        for scene in scenes:
            enhanced_scene = self._enhance_scene_metadata(scene)
            enhanced_scenes.append(enhanced_scene)
        
        # Sort by date
        enhanced_scenes.sort(key=lambda x: x.get('acquisition_date', ''))
        
        return enhanced_scenes
    
    def _enhance_scene_metadata(self, scene: Dict) -> Dict:
        """
        Enhance scene metadata with analysis-ready data info and multispectral outputs.
        
        Args:
            scene: Raw scene metadata from API
            
        Returns:
            Enhanced scene metadata dictionary
        """
        enhanced = scene.copy()
        
        # Add analysis-ready data status
        enhanced['analysis_ready'] = self._check_analysis_ready(scene)
        
        # Add multispectral band information
        enhanced['multispectral_bands'] = self._get_multispectral_info(scene)
        
        # Format acquisition date
        if 'acquisition_date' in scene:
            enhanced['formatted_date'] = scene['acquisition_date']
        
        return enhanced
    
    def _check_analysis_ready(self, scene: Dict) -> Dict:
        """
        Check if scene has analysis-ready data available.
        
        Args:
            scene: Scene metadata
            
        Returns:
            Dictionary with analysis-ready data status
        """
        # Landsat Collection 2 Level-2 products are analysis-ready
        dataset = scene.get('dataset_name', '').lower()
        
        return {
            'is_collection2': 'c2' in dataset,
            'is_level2': 'l2' in dataset,
            'surface_reflectance': 'l2' in dataset,
            'surface_temperature': 'l2' in dataset and 'ot' in dataset,
            'atmospheric_correction': 'l2' in dataset
        }
    
    def _get_multispectral_info(self, scene: Dict) -> Dict:
        """
        Get multispectral band information for the scene.
        
        Args:
            scene: Scene metadata
            
        Returns:
            Dictionary with multispectral band information
        """
        dataset = scene.get('dataset_name', '').lower()
        
        # Landsat 8-9 OLI/TIRS bands
        if 'landsat_ot' in dataset or 'landsat_8' in dataset or 'landsat_9' in dataset:
            return {
                'bands': {
                    'Band 1': 'Coastal/Aerosol (0.43-0.45 µm)',
                    'Band 2': 'Blue (0.45-0.51 µm)',
                    'Band 3': 'Green (0.53-0.59 µm)',
                    'Band 4': 'Red (0.64-0.67 µm)',
                    'Band 5': 'NIR (0.85-0.88 µm)',
                    'Band 6': 'SWIR 1 (1.57-1.65 µm)',
                    'Band 7': 'SWIR 2 (2.11-2.29 µm)',
                    'Band 8': 'Panchromatic (0.50-0.68 µm)',
                    'Band 9': 'Cirrus (1.36-1.38 µm)',
                    'Band 10': 'TIRS 1 (10.6-11.19 µm)',
                    'Band 11': 'TIRS 2 (11.5-12.51 µm)'
                },
                'spatial_resolution': {
                    'multispectral': '30m',
                    'panchromatic': '15m',
                    'thermal': '100m (resampled to 30m)'
                }
            }
        # Landsat 7 ETM+ bands
        elif 'landsat_etm' in dataset or 'landsat_7' in dataset:
            return {
                'bands': {
                    'Band 1': 'Blue (0.45-0.52 µm)',
                    'Band 2': 'Green (0.52-0.60 µm)',
                    'Band 3': 'Red (0.63-0.69 µm)',
                    'Band 4': 'NIR (0.77-0.90 µm)',
                    'Band 5': 'SWIR 1 (1.55-1.75 µm)',
                    'Band 6': 'Thermal (10.40-12.50 µm)',
                    'Band 7': 'SWIR 2 (2.09-2.35 µm)',
                    'Band 8': 'Panchromatic (0.52-0.90 µm)'
                },
                'spatial_resolution': {
                    'multispectral': '30m',
                    'panchromatic': '15m',
                    'thermal': '60m (resampled to 30m)'
                }
            }
        else:
            return {
                'bands': 'Unknown dataset',
                'spatial_resolution': 'Unknown'
            }
    
    def generate_scene_preview(
        self,
        scene: Dict,
        output_dir: str,
        download_full: bool = False
    ) -> Optional[str]:
        """
        Generate a resampled JPEG preview of the scene.
        
        Args:
            scene: Scene metadata dictionary
            output_dir: Output directory for preview images
            download_full: If True, download full scene data
            
        Returns:
            Path to generated preview image or None if failed
        """
        os.makedirs(output_dir, exist_ok=True)
        
        scene_id = scene.get('entity_id', scene.get('display_id', 'unknown'))
        preview_path = os.path.join(output_dir, f"{scene_id}_preview.jpg")
        
        # Try to get browse/thumbnail image
        if 'browse_url' in scene or 'thumbnail_url' in scene:
            import requests
            from PIL import Image
            from io import BytesIO
            
            url = scene.get('browse_url') or scene.get('thumbnail_url')
            if url:
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        
                        # Resample to reasonable size
                        max_size = (1024, 1024)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # Save as JPEG
                        img.convert('RGB').save(preview_path, 'JPEG', quality=85)
                        return preview_path
                except Exception as e:
                    print(f"Warning: Could not download preview for {scene_id}: {e}")
        
        # If download_full is True and we have credentials, download actual scene
        if download_full and self.ee:
            try:
                self.ee.download(scene_id, output_dir)
                print(f"Downloaded full scene: {scene_id}")
            except Exception as e:
                print(f"Warning: Could not download scene {scene_id}: {e}")
        
        return None
    
    def download_scenes(
        self,
        scenes: List[Dict],
        output_dir: str,
        download_previews: bool = True,
        download_full: bool = False
    ):
        """
        Download scene previews and optionally full scenes.
        
        Args:
            scenes: List of scene metadata dictionaries
            output_dir: Output directory for downloads
            download_previews: If True, download preview images
            download_full: If True, download full scene data
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nDownloading {len(scenes)} scenes to {output_dir}...")
        
        for i, scene in enumerate(scenes, 1):
            scene_id = scene.get('entity_id', scene.get('display_id', 'unknown'))
            print(f"\n[{i}/{len(scenes)}] Processing {scene_id}...")
            
            if download_previews:
                preview_path = self.generate_scene_preview(
                    scene, output_dir, download_full=download_full
                )
                if preview_path:
                    print(f"  Preview saved: {preview_path}")
        
        print("\nDownload complete!")
    
    def save_scene_list(self, scenes: List[Dict], output_path: str):
        """
        Save scene list to a JSON file.
        
        Args:
            scenes: List of scene metadata dictionaries
            output_path: Path to output JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(scenes, f, indent=2, default=str)
        print(f"\nScene list saved to: {output_path}")
    
    def print_scene_summary(self, scenes: List[Dict]):
        """
        Print a summary of found scenes.
        
        Args:
            scenes: List of scene metadata dictionaries
        """
        print(f"\n{'='*80}")
        print(f"FOUND {len(scenes)} LANDSAT SCENES")
        print(f"{'='*80}\n")
        
        for i, scene in enumerate(scenes, 1):
            scene_id = scene.get('entity_id', scene.get('display_id', 'Unknown'))
            date = scene.get('acquisition_date', 'Unknown')
            cloud_cover = scene.get('cloud_cover', 'Unknown')
            path = scene.get('wrs_path', 'N/A')
            row = scene.get('wrs_row', 'N/A')
            
            print(f"[{i}] {scene_id}")
            print(f"    Date: {date}")
            print(f"    Path/Row: {path}/{row}")
            print(f"    Cloud Cover: {cloud_cover}%")
            
            # Analysis-ready data info
            if 'analysis_ready' in scene:
                ar = scene['analysis_ready']
                if ar.get('is_level2'):
                    print(f"    Analysis-Ready: Yes (Collection 2 Level-2)")
                    features = []
                    if ar.get('surface_reflectance'):
                        features.append('Surface Reflectance')
                    if ar.get('surface_temperature'):
                        features.append('Surface Temperature')
                    if features:
                        print(f"    Features: {', '.join(features)}")
            
            # Multispectral info
            if 'multispectral_bands' in scene:
                ms = scene['multispectral_bands']
                if isinstance(ms.get('bands'), dict):
                    print(f"    Bands: {len(ms['bands'])} multispectral bands")
                if isinstance(ms.get('spatial_resolution'), dict):
                    res = ms['spatial_resolution']
                    print(f"    Resolution: {res.get('multispectral', 'N/A')} (MS), {res.get('panchromatic', 'N/A')} (Pan)")
            
            print()


def parse_date_range(date_str: str) -> str:
    """
    Parse date string in various formats to YYYY-MM-DD.
    
    Args:
        date_str: Date string in format YYYY-MM-DD, MM/YYYY, or similar
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    # Try YYYY-MM-DD format
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    
    # Try MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%m/%Y')
        return dt.strftime('%Y-%m-01')
    except ValueError:
        pass
    
    # Try YYYY/MM format
    try:
        dt = datetime.strptime(date_str, '%Y/%m')
        return dt.strftime('%Y-%m-01')
    except ValueError:
        pass
    
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or MM/YYYY")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Query Landsat scenes using bounding box and date range'
    )
    
    # Required arguments
    parser.add_argument(
        '--bbox',
        type=float,
        nargs=4,
        metavar=('MIN_LON', 'MIN_LAT', 'MAX_LON', 'MAX_LAT'),
        required=True,
        help='Bounding box coordinates (min_lon min_lat max_lon max_lat)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        required=True,
        help='Start date (YYYY-MM-DD or MM/YYYY)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        required=True,
        help='End date (YYYY-MM-DD or MM/YYYY)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--username',
        type=str,
        help='USGS EarthExplorer username (or set EARTHEXPLORER_USERNAME env var)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='USGS EarthExplorer password (or set EARTHEXPLORER_PASSWORD env var)'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='landsat_ot_c2_l2',
        help='Landsat dataset (default: landsat_ot_c2_l2 for Landsat 8-9 Collection 2 Level-2)'
    )
    parser.add_argument(
        '--max-cloud-cover',
        type=int,
        default=100,
        help='Maximum cloud cover percentage (default: 100)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='landsat_scenes',
        help='Output directory for downloads (default: landsat_scenes)'
    )
    parser.add_argument(
        '--download-previews',
        action='store_true',
        help='Download preview images'
    )
    parser.add_argument(
        '--download-full',
        action='store_true',
        help='Download full scene data (requires credentials)'
    )
    parser.add_argument(
        '--save-json',
        type=str,
        help='Save scene list to JSON file'
    )
    
    args = parser.parse_args()
    
    # Get credentials from args or environment
    username = args.username or os.environ.get('EARTHEXPLORER_USERNAME')
    password = args.password or os.environ.get('EARTHEXPLORER_PASSWORD')
    
    if not username or not password:
        print("Warning: No credentials provided. Some features may be limited.")
        print("Set EARTHEXPLORER_USERNAME and EARTHEXPLORER_PASSWORD environment variables")
        print("or use --username and --password flags.")
        print("You can register at: https://ers.cr.usgs.gov/register/")
        username = None
        password = None
    
    # Parse dates
    try:
        start_date = parse_date_range(args.start_date)
        end_date = parse_date_range(args.end_date)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Create query object
    query = LandsatSceneQuery(username, password)
    
    try:
        # Query scenes
        print(f"\nQuerying Landsat scenes...")
        print(f"  Bounding Box: {args.bbox}")
        print(f"  Date Range: {start_date} to {end_date}")
        print(f"  Dataset: {args.dataset}")
        print(f"  Max Cloud Cover: {args.max_cloud_cover}%")
        
        scenes = query.query_scenes(
            bbox=tuple(args.bbox),
            start_date=start_date,
            end_date=end_date,
            dataset=args.dataset,
            max_cloud_cover=args.max_cloud_cover
        )
        
        # Print summary
        query.print_scene_summary(scenes)
        
        # Save to JSON if requested
        if args.save_json:
            query.save_scene_list(scenes, args.save_json)
        
        # Download previews/full scenes if requested
        if args.download_previews or args.download_full:
            query.download_scenes(
                scenes,
                args.output_dir,
                download_previews=args.download_previews,
                download_full=args.download_full
            )
        
        print(f"\n{'='*80}")
        print(f"Query complete! Found {len(scenes)} scenes.")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        query.disconnect()
    
    return 0


if __name__ == '__main__':
    exit(main())
