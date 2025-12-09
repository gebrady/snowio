# User Data Ingestion and Output Export - Implementation Guide

## Overview

The Jupyter notebook and standalone queries now properly ingest user-drawn polygon data and export query outputs automatically.

## How It Works

### 1. Jupyter Notebook Workflow

#### Step 1: Draw Polygon on Map
```python
from snowio import InteractiveQueryMap
query_map = InteractiveQueryMap()

# Display interactive map with drawing tools
query_map.create_map()
```
- User clicks polygon tool (□) on the map
- Draws polygon by clicking points (max 100 vertices)
- Clicks "Export" button to download GeoJSON
- Saves file as `polygon.geojson`

#### Step 2: Load User-Drawn Polygon
```python
# Load the polygon you just drew and exported
query_map.load_polygon_from_geojson('polygon.geojson')
```
**Output:**
```
✅ Loaded polygon with 5 vertices from polygon.geojson
```

#### Step 3: Query and Display Widgets
```python
# Show query controls (date range, cloud cover, credentials)
query_map.create_widgets()
```
- User fills in parameters
- Clicks "Search Scenes" button
- Results display automatically

#### Step 4: Export Results
```python
# Export query results to JSON
query_map.export_results('landsat_scenes.json')
```
**Output:**
```
✅ Exported 12 scenes to landsat_scenes.json
```

### 2. Standalone Script Workflow

#### Mode 1: Draw and Export Polygon
```bash
python -m snowio.standalone
```

**What happens:**
1. Opens interactive map in browser
2. User draws polygon using drawing tools
3. User clicks "Export" button
4. Saves as `polygon.geojson` in current directory

**Console Output:**
```
================================================================================
❄️  SnowIO: Interactive Landsat Scene Query
================================================================================

Map mode: Draw and export polygon

✅ Interactive map saved to: /tmp/snowio_interactive_map.html

Instructions:
  1. The map will open in your default web browser
  2. Use the drawing tools (□ icon) to draw a polygon
  3. Click the 'Export' button (top right) to download
  4. Save as 'polygon.geojson' in your current directory
  5. Run: python -m snowio.standalone query
```

#### Mode 2: Query with User Polygon
```bash
python -m snowio.standalone query
```

**What happens:**
1. Loads `polygon.geojson` automatically
2. Prompts user for query parameters interactively
3. Runs query with user's polygon and parameters
4. Automatically exports results to `landsat_scenes.json`

**Console Interaction:**
```
✅ Loaded polygon with 5 vertices from polygon.geojson

Enter query parameters:

Start date (YYYY-MM-DD) [2023-06-01]: 2023-06-01
End date (YYYY-MM-DD) [2023-08-31]: 2023-08-31
Max cloud cover % [20]: 20

Dataset options:
  1. Landsat 8 Collection 2 Level 1
  2. Landsat 8 Collection 2 Level 2 (recommended)
  3. Landsat 9 Collection 2 Level 1
  4. Landsat 9 Collection 2 Level 2 (recommended)
Select dataset [2]: 2

USGS Username: your_username
USGS Password: ********

🔍 Searching for Landsat scenes...
   Date range: 2023-06-01 to 2023-08-31
   Max cloud cover: 20%
   Dataset: landsat_ot_c2_l2

✅ Found 12 scenes

Scene ID                              Date         Cloud Cover   Path/Row
================================================================================
LC08_L2SP_066017_20230615_02_T1     2023-06-15   5.2%         066/017
LC08_L2SP_066017_20230701_02_T1     2023-07-01   12.8%        066/017
...

💾 Full results exported to: landsat_scenes.json
```

### 3. Python API Workflow

```python
from snowio import InteractiveQueryMap

# Create instance
qm = InteractiveQueryMap()

# Load user-drawn polygon from GeoJSON
qm.load_polygon_from_geojson('polygon.geojson')

# Query scenes
results = qm.query_scenes(
    polygon_coords=qm.drawn_polygon,
    start_date='2023-06-01',
    end_date='2023-08-31',
    username='your_usgs_username',
    password='your_usgs_password',
    max_cloud_cover=20
)

# Export results
qm.export_results('landsat_scenes.json')
```

## Key Features Implemented

### ✅ User Data Ingestion
- **Method**: `load_polygon_from_geojson(filename)`
- **Supports**: FeatureCollection and single Feature formats
- **Validates**: Maximum 100 vertices
- **Handles**: Polygon, Rectangle, LineString geometries

### ✅ Automatic Output Export
- **Jupyter**: `query_map.export_results(filename)` method
- **Standalone**: Automatically exports to `landsat_scenes.json` after query
- **Format**: JSON with scene metadata (ID, date, cloud cover, path/row, coordinates)

### ✅ Complete Data Flow
```
User draws → Export GeoJSON → Load polygon → Query API → Export results
```

## Output File Formats

### Input: polygon.geojson
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-150.5, 61.5],
            [-149.0, 61.5],
            [-149.0, 60.8],
            [-150.5, 60.8],
            [-150.5, 61.5]
          ]
        ]
      }
    }
  ]
}
```

### Output: landsat_scenes.json
```json
[
  {
    "display_id": "LC08_L2SP_066017_20230615_02_T1",
    "entityId": "LC08_L2SP_066017_20230615_20230621_02_T1",
    "acquisition_date": "2023-06-15",
    "cloud_cover": 5.2,
    "wrs_path": 66,
    "wrs_row": 17,
    "latitude": 61.15,
    "longitude": -149.75
  },
  ...
]
```

## Testing

All functionality tested with 13 unit tests:

```bash
python -m unittest tests.test_interactive_query -v
```

**Results:**
- ✅ test_load_polygon_from_geojson
- ✅ test_load_polygon_from_geojson_invalid_file
- ✅ test_load_polygon_too_many_vertices_from_geojson
- ✅ 10 existing tests (all passing)

**Total: 13/13 tests passing**

## Demo Script

Run the complete workflow demo:

```bash
python demo_workflow.py
```

This demonstrates:
1. Creating a query map
2. Simulating polygon drawing and export
3. Loading polygon from GeoJSON
4. Query configuration
5. Results export

## Summary

**Problem**: Jupyter notebook and standalone queries didn't properly ingest user-drawn polygons or export outputs.

**Solution**: 
- Added `load_polygon_from_geojson()` method to ingest user drawings
- Enhanced standalone script with interactive query mode
- Automatic JSON export of results
- Comprehensive testing (13 tests)
- Complete documentation and demo

**Result**: Users can now:
1. Draw polygons on the map
2. Export as GeoJSON
3. Load back into the system
4. Query Landsat scenes
5. Get results automatically exported

All workflows (Jupyter, standalone, API) now have complete data ingestion and output export capabilities.
