# snowio

Find Landsat scenes and map snow extents with bounding polygon using NDSI (Normalized Difference Snow Index).

## Overview

snowio is a Python toolkit for processing Landsat imagery to analyze snow cover. It calculates NDSI (Normalized Difference Snow Index) from Landsat scenes and classifies pixels into snow, glacier, or unclassified categories.

### NDSI Calculation

The Normalized Difference Snow Index (NDSI) is calculated as:

**NDSI = (Green - SWIR1) / (Green + SWIR1)**

The specific bands used vary by Landsat version:
- **Landsat 4-7**: NDSI = (Band 2 - Band 5) / (Band 2 + Band 5)
- **Landsat 8-9**: NDSI = (Band 3 - Band 6) / (Band 3 + Band 6)

### Classification

The classification output is controlled by the NDSI thresholds provided:

**2-class output** (when only snow threshold is provided):
- **0**: Unclassified (NDSI below snow threshold or invalid data)
- **1**: Snow (NDSI above snow threshold)

**3-class output** (when both snow and ice thresholds are provided):
- **0**: Unclassified (NDSI below snow threshold or invalid data)
- **1**: Snow (NDSI >= snow threshold and < ice threshold)
- **2**: Glacier/Ice (NDSI >= ice threshold)

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Command Line

Process a single Landsat scene (2-class output):

```bash
snowio /path/to/landsat/scene /path/to/output
```

Process with custom snow threshold:

```bash
snowio /path/to/landsat/scene /path/to/output \
  --ndsi-snow-threshold 0.4
```

Process with glacier classification enabled (3-class output):

```bash
snowio /path/to/landsat/scene /path/to/output \
  --ndsi-snow-threshold 0.4 \
  --ndsi-ice-threshold 0.7
```

Process multiple scenes with AOI cropping:

```bash
snowio /path/to/scenes/directory /path/to/output \
  --batch \
  --aoi "minx,miny,maxx,maxy" \
  --ndsi-snow-threshold 0.4 \
  --ndsi-ice-threshold 0.7
```

### Python API

```python
from snowio import process_scene
from shapely.geometry import box

# Define area of interest
aoi = box(-120.5, 38.5, -120.0, 39.0)

# Process scene with 2-class output (snow only)
output_path = process_scene(
    scene_path="/path/to/landsat/scene",
    output_dir="/path/to/output",
    aoi_geometry=aoi,
    ndsi_snow_threshold=0.4
)

# Process scene with 3-class output (snow and glacier)
output_path = process_scene(
    scene_path="/path/to/landsat/scene",
    output_dir="/path/to/output",
    aoi_geometry=aoi,
    ndsi_snow_threshold=0.4,
    ndsi_ice_threshold=0.7
)
```

## Arguments

- `input`: Path to Landsat scene directory or directory containing multiple scenes
- `output`: Output directory for processed layers
- `--aoi`: Area of Interest as WKT string or "minx,miny,maxx,maxy" bounding box (optional)
- `--ndsi-snow-threshold`: NDSI threshold for snow classification (default: 0.4)
- `--ndsi-ice-threshold`: NDSI threshold for glacier/ice classification (optional, enables 3-class output)
- `--ndsi-threshold`: Legacy parameter, use `--ndsi-snow-threshold` instead
- `--glacier-mask`: Legacy parameter for providing glacier mask raster file (deprecated)
- `--batch`: Process multiple scenes from input directory

## Output

The tool generates two output files per scene:
1. `{scene_name}_NDSI.tif`: NDSI values (float, -1 to 1)
2. `{scene_name}_classification.tif`: Classification (uint8)
   - 2-class mode: 0=unclassified, 1=snow
   - 3-class mode: 0=unclassified, 1=snow, 2=glacier/ice

## Requirements

- Python >= 3.7
- rasterio >= 1.3.0
- numpy >= 1.21.0
- shapely >= 2.0.0

## License

MIT
