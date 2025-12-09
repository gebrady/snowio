# SnowIO Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/gebrady/snowio.git
cd snowio

# Install dependencies
pip install -r requirements.txt
```

## Option 1: Jupyter Notebook (Recommended)

The full interactive experience with widgets and controls.

```bash
# Start Jupyter
jupyter notebook interactive_query.ipynb
```

### In the Notebook:

1. **Run the setup cells** to import and initialize the map
2. **Execute the display cell** to show the interactive map
3. **Use the drawing tools** on the map to define your area
4. **Fill in the query parameters:**
   - Start date and end date
   - Cloud cover threshold
   - USGS credentials
5. **Click "Search Scenes"** to query Landsat data
6. **View results** in the output area

## Option 2: Standalone Python Script

Quick map preview and manual querying.

```bash
# Run the standalone script
python -m snowio.standalone
```

This opens an interactive map in your browser where you can:
- Draw polygons
- Export polygon geometry
- Use the API for queries

## Option 3: Python API

For programmatic access in your own scripts.

```python
from snowio import InteractiveQueryMap

# Create instance
qm = InteractiveQueryMap()

# Define area of interest
polygon = [
    [-150.5, 61.5],
    [-149.0, 61.5],
    [-149.0, 60.8],
    [-150.5, 60.8],
    [-150.5, 61.5]
]
qm.set_polygon(polygon)

# Query scenes
results = qm.query_scenes(
    polygon_coords=polygon,
    start_date='2023-06-01',
    end_date='2023-08-31',
    username='your_usgs_username',
    password='your_usgs_password',
    max_cloud_cover=20
)

# Display results
print(f"Found {len(results)} scenes")

# Export to JSON
qm.export_results('scenes.json')
```

## USGS Account Setup

Before querying, you need a free USGS EarthExplorer account:

1. Visit: https://ers.cr.usgs.gov/register
2. Fill out the registration form
3. Verify your email address
4. Use these credentials in the query interface

## Example Queries

### Anchorage Summer Monitoring
```bash
python examples/query_anchorage.py
```

### Denali Winter Monitoring
```bash
python examples/query_denali_winter.py
```

## Map Features

### Basemap Layers
- **OpenStreetMap** - Streets and place names
- **ESRI World Imagery** - RGB satellite imagery
- **Shaded Relief** - Topographic visualization

### Drawing Tools
- **Polygon** - Draw custom shapes (max 100 vertices)
- **Rectangle** - Quick rectangular selection
- **Edit** - Modify vertices
- **Delete** - Remove shapes

### Measurement Tools
- Distance measurement
- Area calculation
- Coordinate display

## Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| Start Date | Beginning of date range | 2023-06-01 |
| End Date | End of date range | 2023-08-31 |
| Cloud Cover | Maximum cloud cover (%) | 20 |
| Dataset | Landsat collection | landsat_ot_c2_l2 |

## Tips

✓ Start with small polygons (4-10 vertices)
✓ Use lower cloud cover for clearer imagery
✓ Expand date range if no results found
✓ Level 2 products are atmospherically corrected
✓ Export results for offline analysis

## Troubleshooting

**No module named 'snowio'**
```bash
# Install in development mode
pip install -e .
# Or set PYTHONPATH
export PYTHONPATH=/path/to/snowio:$PYTHONPATH
```

**Authentication failed**
- Verify USGS credentials
- Check account activation email
- Ensure EarthExplorer access is enabled

**No results found**
- Expand date range
- Increase cloud cover threshold
- Verify polygon covers valid area
- Check coordinate format [lon, lat]

**ImportError: landsatxplore**
```bash
pip install landsatxplore
```

## Next Steps

1. ✅ Create USGS account
2. ✅ Run Jupyter notebook
3. ✅ Draw your area of interest
4. ✅ Query Landsat scenes
5. ✅ Analyze results

For detailed documentation, see:
- [README.md](README.md) - Full documentation
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Visual interface guide
- [examples/](examples/) - Example scripts

## Support

Open an issue on GitHub for questions or problems.
