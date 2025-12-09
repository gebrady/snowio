# snowio
Find Landsat scenes and map snow extents with bounding polygon

## Overview
`snowio` is a tool for querying Landsat satellite scenes using a bounding box Area of Interest (AOI) and date range. It provides:
- Scene search with bounding box and date range filtering
- Analysis-ready data availability information
- Multispectral band metadata
- Preview image generation for scene selection
- Download capability for full scenes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gebrady/snowio.git
cd snowio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Register for USGS EarthExplorer credentials (required for API access):
   - Visit: https://ers.cr.usgs.gov/register/
   - Create a free account

## Available Scripts

The repository includes multiple implementations:

1. **`landsat_query.py`** - **Primary implementation** using direct M2M REST API (credentials required, minimal dependencies)
2. **`landsat_query_m2m.py`** - Alternative M2M implementation (same as primary, kept for backward compatibility)
3. **`landsat_query_landsatxplore.py`** - Legacy implementation using landsatxplore library (may have endpoint issues)

**Recommended:** Use `landsat_query.py` for the most reliable experience.

## Usage

### Basic Query

Query Landsat scenes without downloading:
```bash
python landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --max-cloud-cover 20
```

### Query with Credentials

Set credentials as environment variables:
```bash
export EARTHEXPLORER_USERNAME="your_username"
export EARTHEXPLORER_PASSWORD="your_password"
```

Or pass them directly:
```bash
python landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 01/2023 \
    --end-date 12/2023 \
    --username your_username \
    --password your_password \
    --max-cloud-cover 20
```

### Download Preview Images

Download resampled JPEG previews for scene selection:
```bash
python landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2023-06-01 \
    --end-date 2023-08-31 \
    --download-previews \
    --output-dir ./preview_images \
    --username your_username \
    --password your_password
```

### Download Full Scenes

Download complete scene data:
```bash
python landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2023-06-01 \
    --end-date 2023-06-30 \
    --download-full \
    --output-dir ./landsat_data \
    --username your_username \
    --password your_password
```

### Save Results to JSON

Save scene metadata to JSON for later processing:
```bash
python landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --save-json scenes.json \
    --max-cloud-cover 30
```

## Command Line Arguments

### Required Arguments
- `--bbox MIN_LON MIN_LAT MAX_LON MAX_LAT`: Bounding box coordinates in decimal degrees
- `--start-date`: Start date (formats: YYYY-MM-DD or MM/YYYY)
- `--end-date`: End date (formats: YYYY-MM-DD or MM/YYYY)

### Optional Arguments
- `--username`: USGS EarthExplorer username (or set EARTHEXPLORER_USERNAME env var)
- `--password`: USGS EarthExplorer password (or set EARTHEXPLORER_PASSWORD env var)
- `--dataset`: Landsat dataset identifier (default: landsat_ot_c2_l2)
  - `landsat_ot_c2_l2`: Landsat 8-9 Collection 2 Level-2 (recommended)
  - `landsat_etm_c2_l2`: Landsat 7 Collection 2 Level-2
  - `landsat_tm_c2_l2`: Landsat 4-5 Collection 2 Level-2
- `--max-cloud-cover`: Maximum cloud cover percentage, 0-100 (default: 100)
- `--output-dir`: Output directory for downloads (default: landsat_scenes)
- `--download-previews`: Download preview images for scene selection
- `--download-full`: Download full scene data (requires credentials)
- `--save-json`: Save scene list to JSON file

## Features

### Scene Metadata
Each scene includes:
- Scene ID and display ID
- Acquisition date
- WRS path/row
- Cloud cover percentage
- Browse/thumbnail URLs

### Analysis-Ready Data
Information about analysis-ready data products:
- Collection 2 Level-2 status
- Surface reflectance availability
- Surface temperature availability
- Atmospheric correction status

### Multispectral Bands
Detailed band information including:
- Band names and wavelengths
- Spectral ranges
- Spatial resolution (multispectral, panchromatic, thermal)

### Preview Generation
- Downloads browse/thumbnail images
- Resamples to reasonable size (1024x1024 max)
- Saves as JPEG for quick scene selection
- Organized by scene ID

## Example Output

```
================================================================================
FOUND 12 LANDSAT SCENES
================================================================================

[1] LC08_L2SP_044034_20230615_20230621_02_T1
    Date: 2023-06-15
    Path/Row: 44/34
    Cloud Cover: 8.5%
    Analysis-Ready: Yes (Collection 2 Level-2)
    Features: Surface Reflectance, Surface Temperature
    Bands: 11 multispectral bands
    Resolution: 30m (MS), 15m (Pan)

[2] LC08_L2SP_044034_20230701_20230707_02_T1
    Date: 2023-07-01
    Path/Row: 44/34
    Cloud Cover: 12.3%
    Analysis-Ready: Yes (Collection 2 Level-2)
    Features: Surface Reflectance, Surface Temperature
    Bands: 11 multispectral bands
    Resolution: 30m (MS), 15m (Pan)
...
```

## Datasets

### Landsat 8-9 OLI/TIRS (Operational Land Imager/Thermal Infrared Sensor)
- Dataset ID: `landsat_ot_c2_l2`
- Satellites: Landsat 8, Landsat 9
- Launch dates: 2013 (L8), 2021 (L9)
- Bands: 11 (including panchromatic and thermal)
- Revisit time: 8 days (combined)

### Landsat 7 ETM+ (Enhanced Thematic Mapper Plus)
- Dataset ID: `landsat_etm_c2_l2`
- Satellite: Landsat 7
- Launch date: 1999
- Bands: 8 (including panchromatic and thermal)
- Note: SLC-off issue since 2003 (data gaps in some scenes)

### Landsat 4-5 TM (Thematic Mapper)
- Dataset ID: `landsat_tm_c2_l2`
- Satellites: Landsat 4, Landsat 5
- Mission dates: 1982-2013
- Bands: 7 (including thermal)

## Python API

You can also use the tool programmatically:

```python
from landsat_query import LandsatSceneQuery

# Create query object
query = LandsatSceneQuery(username="your_username", password="your_password")

try:
    # Query scenes
    scenes = query.query_scenes(
        bbox=(-122.5, 37.5, -122.0, 38.0),
        start_date="2023-06-01",
        end_date="2023-08-31",
        dataset="landsat_ot_c2_l2",
        max_cloud_cover=20
    )
    
    # Print summary
    query.print_scene_summary(scenes)
    
    # Download previews
    query.download_scenes(
        scenes,
        output_dir="./previews",
        download_previews=True
    )
    
    # Save to JSON
    query.save_scene_list(scenes, "scenes.json")
    
finally:
    query.disconnect()
```

## License

This project is provided as-is for research and educational purposes.

## Credits

- Uses the USGS Machine-to-Machine (M2M) REST API for direct access
- Optional [landsatxplore](https://github.com/yannforget/landsatxplore) library support for legacy implementation
- Data provided by the U.S. Geological Survey
