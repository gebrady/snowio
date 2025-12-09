# ❄️ SnowIO

**Interactive Landsat Scene Query Tool**

Find Landsat scenes and map snow extents with user-drawn bounding polygons. SnowIO provides an interactive map interface with multiple basemap layers (OSM, RGB imagery, shaded relief) centered on Alaska, allowing users to draw polygons (max 100 vertices), specify date ranges, and query satellite imagery scenes.

## Features

🗺️ **Interactive Mapping**
- Folium-based interactive map centered on Alaska
- Multiple basemap layers:
  - OpenStreetMap (streets and place names)
  - ESRI World Imagery (RGB satellite imagery)
  - ESRI Shaded Relief (topographic visualization)
- Layer control for easy switching

✏️ **Drawing Tools**
- Polygon drawing tool (max 100 vertices)
- Rectangle tool for quick area selection
- Edit and delete capabilities
- Visual measurement tools

📅 **Query Parameters**
- Date range selection with date pickers
- Cloud cover filtering (0-100%)
- Multiple Landsat dataset options (Landsat 8/9, Level 1/2)
- Real-time scene search

🛰️ **Landsat Integration**
- Search Landsat 8 and 9 scenes
- Filter by cloud cover and date
- View scene metadata (ID, date, path/row)
- Export results to JSON

## Installation

### From source:

```bash
git clone https://github.com/gebrady/snowio.git
cd snowio
pip install -r requirements.txt
pip install -e .
```

### Requirements:
- Python >= 3.8
- folium >= 0.14.0
- ipywidgets >= 8.0.0
- jupyter >= 1.0.0
- landsatxplore >= 0.14.0
- requests >= 2.28.0
- shapely >= 2.0.0

## USGS EarthExplorer Account

To query Landsat data, you need a free USGS EarthExplorer account:

1. Register at: https://ers.cr.usgs.gov/register
2. Verify your email address
3. Use your credentials in the query interface

## Usage

### Option 1: Jupyter Notebook (Recommended)

The Jupyter notebook provides the full interactive experience with widgets:

```bash
jupyter notebook interactive_query.ipynb
```

**Workflow:**
1. Run the notebook cells to initialize the map
2. Use the drawing tools to define your area of interest
3. Select date range and other parameters
4. Enter your USGS credentials
5. Click "Search Scenes" to query
6. View results in the interactive table
7. Export results if needed

### Option 2: Standalone Script

For a quick map preview without widgets:

```bash
python -m snowio.standalone
```

This opens an interactive map in your browser where you can:
- Draw polygons
- Export polygon geometry
- Use the Python API for queries

### Option 3: Python API

Use SnowIO programmatically in your Python scripts:

```python
from snowio import InteractiveQueryMap

# Create query map instance
query_map = InteractiveQueryMap()

# Define your area of interest (max 100 vertices)
# Coordinates: [longitude, latitude]
polygon = [
    [-150.5, 61.5],   # Northwest corner
    [-149.0, 61.5],   # Northeast corner
    [-149.0, 60.8],   # Southeast corner
    [-150.5, 60.8],   # Southwest corner
    [-150.5, 61.5]    # Close polygon
]

query_map.set_polygon(polygon)

# Query Landsat scenes
results = query_map.query_scenes(
    polygon_coords=polygon,
    start_date='2023-06-01',
    end_date='2023-08-31',
    username='your_usgs_username',
    password='your_usgs_password',
    dataset='landsat_ot_c2_l2',  # Landsat 8/9 Collection 2 Level 2
    max_cloud_cover=20
)

# Display results
print(f"Found {len(results)} scenes")
for scene in results:
    print(f"  {scene['display_id']} - {scene['acquisition_date']} - {scene['cloud_cover']}% cloud")

# Export to JSON
query_map.export_results('my_landsat_scenes.json')
```

## Map Features

### Drawing Tools
- **Polygon Tool**: Click multiple points to create a custom polygon (max 100 vertices)
- **Rectangle Tool**: Click and drag to create a rectangular area
- **Edit Tool**: Modify existing polygons by dragging vertices
- **Delete Tool**: Remove drawn polygons
- **Measure Tool**: Measure distances and areas

### Basemap Layers
- **OpenStreetMap**: Best for identifying place names, roads, and boundaries
- **ESRI World Imagery**: High-resolution RGB satellite imagery
- **Shaded Relief**: Topographic visualization showing elevation and terrain

### Additional Controls
- **Fullscreen**: Expand map to fullscreen mode
- **Mouse Position**: Display current cursor coordinates
- **Layer Control**: Toggle between different basemaps

## Query Parameters

### Dataset Options
- `landsat_ot_c2_l1`: Landsat 8/9 Collection 2 Level 1 (top-of-atmosphere)
- `landsat_ot_c2_l2`: Landsat 8/9 Collection 2 Level 2 (surface reflectance, recommended)

### Date Range
- Landsat 8: Launched February 2013
- Landsat 9: Launched September 2021
- Historical Landsat archive available for earlier missions

### Cloud Cover
- 0-100% range
- Lower values provide clearer imagery but fewer results
- Consider seasonal patterns in Alaska (more clouds in summer)

## Examples

### Example 1: Anchorage Area - Summer Snow Melt

```python
from snowio import InteractiveQueryMap

qm = InteractiveQueryMap()

# Polygon around Anchorage
anchorage = [
    [-150.5, 61.5],
    [-149.0, 61.5],
    [-149.0, 60.8],
    [-150.5, 60.8],
    [-150.5, 61.5]
]

qm.set_polygon(anchorage)

# Query summer scenes for snow melt analysis
results = qm.query_scenes(
    polygon_coords=anchorage,
    start_date='2023-06-01',
    end_date='2023-08-31',
    username='your_username',
    password='your_password',
    max_cloud_cover=10  # Low cloud cover for clear imagery
)

print(f"Found {len(results)} scenes for summer snow melt analysis")
```

### Example 2: Denali Region - Winter Monitoring

```python
from snowio import InteractiveQueryMap

qm = InteractiveQueryMap()

# Polygon around Denali
denali = [
    [-151.5, 63.5],
    [-150.0, 63.5],
    [-150.0, 62.8],
    [-151.5, 62.8],
    [-151.5, 63.5]
]

qm.set_polygon(denali)

# Query winter scenes
results = qm.query_scenes(
    polygon_coords=denali,
    start_date='2023-11-01',
    end_date='2024-03-31',
    username='your_username',
    password='your_password',
    max_cloud_cover=30  # Higher tolerance for winter clouds
)

print(f"Found {len(results)} scenes for winter monitoring")
```

## Limitations

- **Polygon Vertices**: Maximum 100 vertices per polygon
- **Query Results**: Maximum 100 scenes per query (USGS API limit)
- **API Rate Limits**: USGS EarthExplorer has rate limiting
- **Geographic Focus**: Map defaults to Alaska, but works globally

## Troubleshooting

### Authentication Errors
- Verify your USGS EarthExplorer credentials
- Ensure your account is activated (check email)
- Check if the USGS API is operational

### No Results Found
- Expand your date range
- Increase cloud cover threshold
- Check if your polygon covers a valid area
- Verify coordinates are in [longitude, latitude] format

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs >= 3.8)

### Jupyter Issues
- Install Jupyter extensions: `jupyter nbextension enable --py widgetsnbextension`
- Restart Jupyter kernel if widgets don't display

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License

## Acknowledgments

- **USGS**: For providing free Landsat data through EarthExplorer
- **Folium**: For interactive mapping capabilities
- **landsatxplore**: For simplified Landsat API access

## Contact

For questions or issues, please open an issue on GitHub.
