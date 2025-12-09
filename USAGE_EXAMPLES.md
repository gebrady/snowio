# Landsat Scene Query Tool - Usage Examples

## Example 1: Basic Query (No Credentials Needed)

Query Landsat scenes for a bounding box without downloading:

```bash
python3 landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --max-cloud-cover 20 \
    --save-json scenes.json
```

This will:
- Search for scenes in the San Francisco Bay Area
- Filter to scenes with ≤20% cloud cover
- Save results to `scenes.json`

## Example 2: Query with Preview Downloads

Download preview images for scene selection:

```bash
export EARTHEXPLORER_USERNAME="your_username"
export EARTHEXPLORER_PASSWORD="your_password"

python3 landsat_query_m2m.py \
    --bbox -106.0 39.5 -105.5 40.0 \
    --start-date 06/2023 \
    --end-date 08/2023 \
    --max-cloud-cover 15 \
    --download-previews \
    --output-dir ./preview_images \
    --save-json summer_scenes.json
```

This will:
- Search Colorado Rocky Mountains
- Download JPEG previews to `./preview_images/`
- Save metadata to `summer_scenes.json`

## Example 3: Snow Extent Mapping

Query winter scenes for snow analysis:

```bash
python3 landsat_query.py \
    --bbox -120.0 38.0 -119.0 39.0 \
    --start-date 12/2022 \
    --end-date 03/2023 \
    --max-cloud-cover 10 \
    --dataset landsat_ot_c2_l2 \
    --download-previews \
    --output-dir ./winter_scenes \
    --save-json winter_snow.json
```

This targets Yosemite/Sierra Nevada for winter snow extent mapping.

## Example 4: Multi-Year Analysis

Query multiple years of data:

```bash
# Year 1
python3 landsat_query_m2m.py \
    --bbox -105.5 40.0 -105.0 40.5 \
    --start-date 2020-01-01 \
    --end-date 2020-12-31 \
    --max-cloud-cover 20 \
    --save-json scenes_2020.json

# Year 2
python3 landsat_query_m2m.py \
    --bbox -105.5 40.0 -105.0 40.5 \
    --start-date 2021-01-01 \
    --end-date 2021-12-31 \
    --max-cloud-cover 20 \
    --save-json scenes_2021.json
```

## Example 5: Different Datasets

Query Landsat 7 scenes (for historical data):

```bash
python3 landsat_query.py \
    --bbox -122.5 37.5 -122.0 38.0 \
    --start-date 2010-01-01 \
    --end-date 2010-12-31 \
    --dataset landsat_etm_c2_l2 \
    --max-cloud-cover 30 \
    --save-json landsat7_scenes.json
```

## Python API Usage

```python
from landsat_query import LandsatSceneQuery
import os

# Set credentials
username = os.environ.get('EARTHEXPLORER_USERNAME')
password = os.environ.get('EARTHEXPLORER_PASSWORD')

# Create query instance
query = LandsatSceneQuery(username, password)

try:
    # Query scenes
    scenes = query.query_scenes(
        bbox=(-122.5, 37.5, -122.0, 38.0),
        start_date="2023-06-01",
        end_date="2023-08-31",
        max_cloud_cover=20
    )
    
    # Print summary
    query.print_scene_summary(scenes)
    
    # Download previews
    query.download_scenes(
        scenes,
        output_dir="./my_previews",
        download_previews=True
    )
    
    # Save metadata
    query.save_scene_list(scenes, "my_scenes.json")
    
    # Process individual scenes
    for scene in scenes:
        print(f"Scene: {scene['entity_id']}")
        print(f"  Date: {scene['acquisition_date']}")
        print(f"  Cloud: {scene['cloud_cover']}%")
        print(f"  Analysis Ready: {scene['analysis_ready']['is_level2']}")
        
finally:
    query.disconnect()
```

## Common Bounding Boxes

```python
# Major US regions
san_francisco = (-122.5, 37.5, -122.0, 38.0)
rocky_mountains = (-106.0, 39.0, -105.0, 40.0)
yosemite = (-120.0, 37.5, -119.0, 38.5)
yellowstone = (-111.0, 44.0, -110.0, 45.0)
seattle = (-122.5, 47.0, -122.0, 48.0)

# To use:
python3 landsat_query.py --bbox -122.5 37.5 -122.0 38.0 ...
```

## Output Files

After running queries, you'll have:

1. **JSON metadata file** (e.g., `scenes.json`):
   - Scene IDs and display IDs
   - Acquisition dates
   - Cloud cover percentages
   - Analysis-ready data status
   - Multispectral band information
   - Browse URLs

2. **Preview images** (if `--download-previews` used):
   - `{scene_id}_preview.jpg` files
   - Resampled to 1024x1024 max
   - Ready for visual inspection

## Tips

1. **Start with conservative cloud cover**: Use `--max-cloud-cover 20` or lower for best results
2. **Use month/year format for ranges**: `--start-date 01/2023 --end-date 12/2023`
3. **Check previews before full download**: Always use `--download-previews` first to select scenes
4. **Landsat 8-9 for recent data**: Use `--dataset landsat_ot_c2_l2` (default)
5. **Landsat 7 for 1999-present**: Use `--dataset landsat_etm_c2_l2`
6. **Save JSON for later processing**: Always use `--save-json` to preserve metadata
