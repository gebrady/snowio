#!/usr/bin/env python3
"""
Landsat Scene Query Tool
Query Landsat scenes using a bounding box AOI and date range.
Uses direct USGS Machine-to-Machine (M2M) REST API.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse


class LandsatAPI:
    """
    Direct implementation of USGS Machine-to-Machine (M2M) API for Landsat queries.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the M2M API client.
        
        Args:
            username: USGS EarthExplorer username
            password: USGS EarthExplorer password
        """
        self.username = username
        self.password = password
        self.api_key = None
        self.base_url = "https://m2m.cr.usgs.gov/api/api/json/stable"
        self.session = requests.Session()
        
    def login(self):
        """Login and obtain API key."""
        if not self.username or not self.password:
            raise ValueError("Username and password required")
        
        url = f"{self.base_url}/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('errorCode'):
            raise Exception(f"Login failed: {data.get('errorMessage')}")
        
        self.api_key = data['data']
        return self.api_key
    
    def logout(self):
        """Logout and invalidate API key."""
        if self.api_key:
            url = f"{self.base_url}/logout"
            payload = {"apiKey": self.api_key}
            try:
                self.session.post(url, json=payload)
            except Exception:
                # Ignore errors during logout
                pass
            self.api_key = None
    
    def search_scenes(
        self,
        dataset_name: str,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        max_cloud_cover: int = 100,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search for Landsat scenes.
        
        Args:
            dataset_name: Dataset identifier (e.g., 'landsat_ot_c2_l2')
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cloud_cover: Maximum cloud cover (0-100)
            max_results: Maximum number of results
            
        Returns:
            List of scene metadata dictionaries
        """
        if not self.api_key:
            self.login()
        
        url = f"{self.base_url}/scene-search"
        
        # Build spatial filter
        min_lon, min_lat, max_lon, max_lat = bbox
        spatial_filter = {
            "filterType": "mbr",
            "lowerLeft": {"latitude": min_lat, "longitude": min_lon},
            "upperRight": {"latitude": max_lat, "longitude": max_lon}
        }
        
        # Build acquisition filter
        acquisition_filter = {
            "start": start_date,
            "end": end_date
        }
        
        # Build cloud cover filter
        cloud_cover_filter = {
            "min": 0,
            "max": max_cloud_cover,
            "includeUnknown": False
        }
        
        payload = {
            "apiKey": self.api_key,
            "datasetName": dataset_name,
            "maxResults": max_results,
            "spatialFilter": spatial_filter,
            "temporalFilter": acquisition_filter,
            "sceneFilter": {
                "cloudCoverFilter": cloud_cover_filter
            }
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('errorCode'):
            raise Exception(f"Search failed: {data.get('errorMessage')}")
        
        return data.get('data', {}).get('results', [])
    
    def get_download_options(self, dataset_name: str, entity_ids: List[str]) -> Dict:
        """Get download options for scenes."""
        if not self.api_key:
            self.login()
        
        url = f"{self.base_url}/download-options"
        payload = {
            "apiKey": self.api_key,
            "datasetName": dataset_name,
            "entityIds": entity_ids
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('errorCode'):
            raise Exception(f"Get download options failed: {data.get('errorMessage')}")
        
        return data.get('data', [])
    
    def request_download(self, downloads: List[Dict]) -> Dict:
        """Request download URLs for scenes."""
        if not self.api_key:
            self.login()
        
        url = f"{self.base_url}/download-request"
        payload = {
            "apiKey": self.api_key,
            "downloads": downloads
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('errorCode'):
            raise Exception(f"Download request failed: {data.get('errorMessage')}")
        
        return data.get('data', {})


class LandsatSceneQuery:
    """
    Query and download Landsat scenes using M2M API.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize the query tool."""
        self.api = LandsatAPI(username, password)
        
    def connect(self):
        """Connect to the API."""
        self.api.login()
        
    def disconnect(self):
        """Disconnect from the API."""
        self.api.logout()
    
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
        scenes = self.api.search_scenes(
            dataset_name=dataset,
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=max_cloud_cover
        )
        
        # Enhance scene metadata
        enhanced_scenes = []
        for scene in scenes:
            enhanced_scene = self._enhance_scene_metadata(scene, dataset)
            enhanced_scenes.append(enhanced_scene)
        
        # Sort by date
        enhanced_scenes.sort(key=lambda x: x.get('acquisition_date', ''))
        
        return enhanced_scenes
    
    def _enhance_scene_metadata(self, scene: Dict, dataset: str) -> Dict:
        """Enhance scene metadata with analysis-ready data info."""
        enhanced = scene.copy()
        
        # Extract key fields
        enhanced['entity_id'] = scene.get('entityId', '')
        enhanced['display_id'] = scene.get('displayId', '')
        enhanced['acquisition_date'] = scene.get('temporalCoverage', {}).get('startDate', '')[:10]
        enhanced['cloud_cover'] = scene.get('cloudCover', 0)
        
        # Extract path/row from metadata
        spatial_bounds = scene.get('spatialBounds', {})
        enhanced['bounds'] = spatial_bounds
        
        # Add analysis-ready data status
        enhanced['analysis_ready'] = self._check_analysis_ready(dataset)
        
        # Add multispectral band information
        enhanced['multispectral_bands'] = self._get_multispectral_info(dataset)
        
        # Add browse URL if available
        browse = scene.get('browse', [])
        if browse:
            enhanced['browse_url'] = browse[0].get('browsePath', '')
        
        return enhanced
    
    def _check_analysis_ready(self, dataset: str) -> Dict:
        """Check if dataset has analysis-ready data."""
        dataset_lower = dataset.lower()
        
        return {
            'is_collection2': 'c2' in dataset_lower,
            'is_level2': 'l2' in dataset_lower,
            'surface_reflectance': 'l2' in dataset_lower,
            'surface_temperature': 'l2' in dataset_lower and 'ot' in dataset_lower,
            'atmospheric_correction': 'l2' in dataset_lower
        }
    
    def _get_multispectral_info(self, dataset: str) -> Dict:
        """Get multispectral band information."""
        dataset_lower = dataset.lower()
        
        if 'landsat_ot' in dataset_lower or 'landsat_8' in dataset_lower or 'landsat_9' in dataset_lower:
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
        elif 'landsat_etm' in dataset_lower or 'landsat_7' in dataset_lower:
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
    
    def generate_scene_preview(self, scene: Dict, output_dir: str) -> Optional[str]:
        """Generate preview image from browse URL."""
        from PIL import Image
        from io import BytesIO
        
        os.makedirs(output_dir, exist_ok=True)
        
        scene_id = scene.get('entity_id', scene.get('display_id', 'unknown'))
        preview_path = os.path.join(output_dir, f"{scene_id}_preview.jpg")
        
        browse_url = scene.get('browse_url')
        if browse_url:
            try:
                response = requests.get(browse_url, timeout=30)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    
                    # Resample to reasonable size
                    max_size = (1024, 1024)
                    # Use LANCZOS for backward compatibility with older Pillow versions
                    if hasattr(Image, 'Resampling'):
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    else:
                        img.thumbnail(max_size, Image.LANCZOS)
                    
                    # Save as JPEG
                    img.convert('RGB').save(preview_path, 'JPEG', quality=85)
                    return preview_path
            except Exception as e:
                print(f"Warning: Could not download preview for {scene_id}: {e}")
        
        return None
    
    def download_scenes(
        self,
        scenes: List[Dict],
        output_dir: str,
        download_previews: bool = True
    ):
        """Download scene previews."""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nDownloading {len(scenes)} scene previews to {output_dir}...")
        
        for i, scene in enumerate(scenes, 1):
            scene_id = scene.get('entity_id', scene.get('display_id', 'unknown'))
            print(f"\n[{i}/{len(scenes)}] Processing {scene_id}...")
            
            if download_previews:
                preview_path = self.generate_scene_preview(scene, output_dir)
                if preview_path:
                    print(f"  Preview saved: {preview_path}")
        
        print("\nDownload complete!")
    
    def save_scene_list(self, scenes: List[Dict], output_path: str):
        """Save scene list to JSON."""
        with open(output_path, 'w') as f:
            json.dump(scenes, f, indent=2, default=str)
        print(f"\nScene list saved to: {output_path}")
    
    def print_scene_summary(self, scenes: List[Dict]):
        """Print scene summary."""
        print(f"\n{'='*80}")
        print(f"FOUND {len(scenes)} LANDSAT SCENES")
        print(f"{'='*80}\n")
        
        for i, scene in enumerate(scenes, 1):
            scene_id = scene.get('entity_id', scene.get('display_id', 'Unknown'))
            date = scene.get('acquisition_date', 'Unknown')
            cloud_cover = scene.get('cloud_cover', 'Unknown')
            
            print(f"[{i}] {scene_id}")
            print(f"    Date: {date}")
            print(f"    Display ID: {scene.get('display_id', 'N/A')}")
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
    """Parse date string to YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    
    try:
        dt = datetime.strptime(date_str, '%m/%Y')
        return dt.strftime('%Y-%m-01')
    except ValueError:
        pass
    
    try:
        dt = datetime.strptime(date_str, '%Y/%m')
        return dt.strftime('%Y-%m-01')
    except ValueError:
        pass
    
    raise ValueError(f"Invalid date format: {date_str}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Query Landsat scenes using M2M API'
    )
    
    parser.add_argument('--bbox', type=float, nargs=4, required=True,
                       metavar=('MIN_LON', 'MIN_LAT', 'MAX_LON', 'MAX_LAT'),
                       help='Bounding box coordinates')
    parser.add_argument('--start-date', type=str, required=True,
                       help='Start date (YYYY-MM-DD or MM/YYYY)')
    parser.add_argument('--end-date', type=str, required=True,
                       help='End date (YYYY-MM-DD or MM/YYYY)')
    parser.add_argument('--username', type=str,
                       help='USGS EarthExplorer username')
    parser.add_argument('--password', type=str,
                       help='USGS EarthExplorer password')
    parser.add_argument('--dataset', type=str, default='landsat_ot_c2_l2',
                       help='Landsat dataset')
    parser.add_argument('--max-cloud-cover', type=int, default=100,
                       help='Maximum cloud cover percentage')
    parser.add_argument('--output-dir', type=str, default='landsat_scenes',
                       help='Output directory')
    parser.add_argument('--download-previews', action='store_true',
                       help='Download preview images')
    parser.add_argument('--save-json', type=str,
                       help='Save scene list to JSON')
    
    args = parser.parse_args()
    
    username = args.username or os.environ.get('EARTHEXPLORER_USERNAME')
    password = args.password or os.environ.get('EARTHEXPLORER_PASSWORD')
    
    if not username or not password:
        print("Error: Credentials required for M2M API")
        print("Set EARTHEXPLORER_USERNAME and EARTHEXPLORER_PASSWORD")
        return 1
    
    try:
        start_date = parse_date_range(args.start_date)
        end_date = parse_date_range(args.end_date)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    query = LandsatSceneQuery(username, password)
    
    try:
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
        
        query.print_scene_summary(scenes)
        
        if args.save_json:
            query.save_scene_list(scenes, args.save_json)
        
        if args.download_previews:
            query.download_scenes(scenes, args.output_dir, download_previews=True)
        
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
