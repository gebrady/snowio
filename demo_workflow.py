#!/usr/bin/env python3
"""
Demo script showing the complete workflow of:
1. Drawing a polygon on the map
2. Exporting it to GeoJSON
3. Loading it back
4. Querying Landsat scenes
5. Exporting results
"""

from snowio import InteractiveQueryMap
import json

print("=" * 80)
print("SnowIO Complete Workflow Demo")
print("=" * 80)
print()

# Step 1: Create the query map
print("Step 1: Creating interactive query map...")
qm = InteractiveQueryMap()
print("✅ Query map created")
print()

# Step 2: Simulate user drawing a polygon (in real use, user draws on map)
print("Step 2: Setting up a polygon (simulating user drawing)...")
print("   In the real workflow:")
print("   - User draws polygon on the interactive map")
print("   - User clicks Export button")
print("   - Saves as polygon.geojson")
print()

# Create a sample polygon for Anchorage, Alaska
sample_polygon = [
    [-150.5, 61.5],
    [-149.0, 61.5],
    [-149.0, 60.8],
    [-150.5, 60.8],
    [-150.5, 61.5]
]

# Save it as GeoJSON (simulating user export)
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [sample_polygon]
            }
        }
    ]
}

with open('demo_polygon.geojson', 'w') as f:
    json.dump(geojson_data, f, indent=2)

print("✅ Sample polygon saved as demo_polygon.geojson")
print(f"   Area: Anchorage, Alaska region")
print(f"   Vertices: {len(sample_polygon)}")
print()

# Step 3: Load the polygon from GeoJSON
print("Step 3: Loading polygon from GeoJSON file...")
qm.load_polygon_from_geojson('demo_polygon.geojson')
print(f"   Bounds: {qm.drawn_polygon[0]} to {qm.drawn_polygon[2]}")
print()

# Step 4: Show how to query (without actually querying)
print("Step 4: Query configuration...")
print("   To query Landsat scenes, run:")
print()
print("   results = qm.query_scenes(")
print("       polygon_coords=qm.drawn_polygon,")
print("       start_date='2023-06-01',")
print("       end_date='2023-08-31',")
print("       username='your_usgs_username',")
print("       password='your_usgs_password',")
print("       max_cloud_cover=20")
print("   )")
print()

# Step 5: Simulate results export
print("Step 5: Exporting results...")
print("   After querying, export results with:")
print("   qm.export_results('landsat_scenes.json')")
print()

# Show the complete workflow summary
print("=" * 80)
print("Complete Workflow Summary")
print("=" * 80)
print()
print("📍 Jupyter Notebook Workflow:")
print("   1. Run: query_map.create_map() - displays map")
print("   2. Draw polygon on the map using drawing tools")
print("   3. Click Export button, save as polygon.geojson")
print("   4. Run: query_map.load_polygon_from_geojson('polygon.geojson')")
print("   5. Run: query_map.create_widgets() - displays query controls")
print("   6. Fill in parameters and click 'Search Scenes'")
print("   7. Run: query_map.export_results('landsat_scenes.json')")
print()
print("🖥️  Standalone Script Workflow:")
print("   1. Run: python -m snowio.standalone")
print("      - Opens map in browser, draw and export polygon")
print("   2. Run: python -m snowio.standalone query")
print("      - Prompts for parameters, queries scenes, exports results")
print()
print("🐍 Python API Workflow:")
print("   1. Create: qm = InteractiveQueryMap()")
print("   2. Load polygon: qm.load_polygon_from_geojson('polygon.geojson')")
print("   3. Query: results = qm.query_scenes(...)")
print("   4. Export: qm.export_results('landsat_scenes.json')")
print()
print("=" * 80)
print("✅ Demo completed! Check demo_polygon.geojson")
print("=" * 80)
