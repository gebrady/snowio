# SnowIO Visual Guide

## Interactive Map Features

The SnowIO interactive query map provides a comprehensive interface for querying Landsat satellite scenes over Alaska and other regions.

### Map Visualization

The map is centered on Alaska (64.0°N, 152.0°W) at zoom level 4, providing a view of the entire state.

### Available Basemap Layers

1. **OpenStreetMap** - Default layer with streets and place names
2. **ESRI World Imagery** - High-resolution RGB satellite imagery
3. **Shaded Relief** - Topographic visualization showing terrain elevation

Use the layer control button (top-right corner) to switch between layers.

### Drawing Tools

Located on the left side of the map:

- **Polygon Tool** ✏️ - Draw custom polygons (click points, max 100 vertices)
- **Rectangle Tool** ▢ - Quick rectangular area selection (click and drag)
- **Edit Tool** ✎ - Modify existing shapes by dragging vertices
- **Delete Tool** 🗑️ - Remove drawn shapes

### Additional Controls

- **Fullscreen** 🔍 - Expand map to fullscreen (top-right)
- **Mouse Position** 📍 - Shows current coordinates at bottom
- **Measure Tool** 📏 - Measure distances and areas (left side)
- **Layer Control** 🗺️ - Toggle between basemaps (top-right)
- **Export** 💾 - Export drawn polygons as GeoJSON

### Query Workflow

1. **Draw Polygon**
   - Click the polygon tool (□ icon)
   - Click multiple points on the map to define your area
   - Double-click to finish
   - Maximum 100 vertices allowed

2. **Set Parameters** (in Jupyter notebook)
   - Start Date: Select beginning of date range
   - End Date: Select end of date range
   - Cloud Cover: Adjust slider (0-100%)
   - Dataset: Choose Landsat 8 or 9, Level 1 or 2
   - Credentials: Enter USGS EarthExplorer username/password

3. **Search Scenes**
   - Click "Search Scenes" button
   - Wait for query to complete
   - Results displayed in interactive table

4. **View Results**
   - Scene ID, date, cloud cover, path/row shown
   - Export results to JSON for further analysis
   - View scene locations on map

### Example Usage

#### Alaska Region Selection
```
Anchorage Area:
- Northwest: -150.5°, 61.5°
- Northeast: -149.0°, 61.5°
- Southeast: -149.0°, 60.8°
- Southwest: -150.5°, 60.8°

Denali Region:
- Northwest: -151.5°, 63.5°
- Northeast: -150.0°, 63.5°
- Southeast: -150.0°, 62.8°
- Southwest: -151.5°, 62.8°
```

#### Date Range Examples
```
Summer Snow Melt: June 1 - August 31
Winter Monitoring: November 1 - March 31
Annual Analysis: January 1 - December 31
```

#### Cloud Cover Guidelines
```
Clear Imagery: 0-10%
Good Quality: 10-20%
Acceptable: 20-40%
Winter (higher tolerance): 30-50%
```

### Map Controls Reference

| Control | Location | Function |
|---------|----------|----------|
| Zoom In/Out | Top-left | Adjust map zoom level |
| Draw Polygon | Left side | Draw custom polygon |
| Draw Rectangle | Left side | Draw rectangle |
| Edit Shape | Left side | Modify vertices |
| Delete Shape | Left side | Remove shapes |
| Measure | Left side | Measure distance/area |
| Layer Control | Top-right | Switch basemaps |
| Fullscreen | Top-right | Toggle fullscreen |
| Export | Top-right | Export GeoJSON |
| Mouse Position | Bottom | Show coordinates |

### Keyboard Shortcuts

- **Escape** - Cancel current drawing
- **Delete/Backspace** - Remove selected shape
- **Ctrl/Cmd + Z** - Undo (in edit mode)

### Tips for Best Results

1. **Layer Selection**
   - Use OpenStreetMap to identify place names
   - Switch to Imagery to see actual satellite view
   - Use Shaded Relief to understand terrain

2. **Polygon Drawing**
   - Start with simple polygons (4-10 vertices)
   - Keep polygon boundaries within your area of interest
   - Avoid self-intersecting polygons

3. **Query Optimization**
   - Narrow date ranges for faster results
   - Lower cloud cover = fewer but clearer scenes
   - Level 2 products are atmospherically corrected

4. **Result Analysis**
   - Export results to JSON for offline analysis
   - Note path/row for consistent scene coverage
   - Check acquisition dates for seasonal patterns

### Technical Details

**Map Library:** Folium (Python wrapper for Leaflet.js)
**Coordinate System:** WGS84 (EPSG:4326)
**Map Projection:** Web Mercator (EPSG:3857)
**Data Source:** USGS EarthExplorer / Landsat Archive
**Satellite Data:** Landsat 8 (2013-present), Landsat 9 (2021-present)

### File Formats

**Input:**
- Polygon coordinates: [[lon, lat], [lon, lat], ...]
- Date format: YYYY-MM-DD
- Coordinate format: Decimal degrees

**Output:**
- Results: JSON format
- Map: HTML file (standalone)
- Polygons: GeoJSON format

### Common Issues and Solutions

**Issue:** Drawing tool not responding
**Solution:** Ensure you've selected the polygon/rectangle tool first

**Issue:** Too many vertices error
**Solution:** Simplify polygon or split into multiple queries

**Issue:** No results found
**Solution:** Expand date range or increase cloud cover threshold

**Issue:** Authentication failed
**Solution:** Verify USGS credentials and account activation

**Issue:** Map not loading
**Solution:** Check internet connection for tile servers
