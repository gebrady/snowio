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

Output classification values:
- **0**: Unclassified (NDSI below threshold or invalid data)
- **1**: Snow (NDSI above threshold, not in glacier area)
- **2**: Glacier (NDSI above threshold, in glaciated area)

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Command Line

Process a single Landsat scene:

```bash
snowio /path/to/landsat/scene /path/to/output
```

Process multiple scenes with AOI cropping:

```bash
snowio /path/to/scenes/directory /path/to/output \
  --batch \
  --aoi "minx,miny,maxx,maxy" \
  --ndsi-threshold 0.4
```

With glacier mask:

```bash
snowio /path/to/landsat/scene /path/to/output \
  --aoi "POLYGON((...))" \
  --glacier-mask /path/to/glacier_mask.tif \
  --ndsi-threshold 0.4
```

### Python API

```python
from snowio import process_scene
from shapely.geometry import box

# Define area of interest
aoi = box(-120.5, 38.5, -120.0, 39.0)

# Process scene
output_path = process_scene(
    scene_path="/path/to/landsat/scene",
    output_dir="/path/to/output",
    aoi_geometry=aoi,
    ndsi_threshold=0.4
)
```

## Arguments

- `input`: Path to Landsat scene directory or directory containing multiple scenes
- `output`: Output directory for processed layers
- `--aoi`: Area of Interest as WKT string or "minx,miny,maxx,maxy" bounding box (optional)
- `--glacier-mask`: Path to glacier mask raster file (optional)
- `--ndsi-threshold`: NDSI threshold for snow classification (default: 0.4)
- `--batch`: Process multiple scenes from input directory

## Output

The tool generates two output files per scene:
1. `{scene_name}_NDSI.tif`: NDSI values (float, -1 to 1)
2. `{scene_name}_classification.tif`: Classification (uint8, 0/1/2)

## Requirements

- Python >= 3.7
- rasterio >= 1.3.0
- numpy >= 1.21.0
- shapely >= 2.0.0

## License

MIT
