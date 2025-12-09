#!/usr/bin/env python3
"""
Standalone script for interactive Landsat scene query.
This version can be run outside of Jupyter notebooks.
"""

from snowio import InteractiveQueryMap
import webbrowser
import os
import tempfile


def main():
    """
    Main function to run the interactive query in a web browser.
    """
    print("=" * 80)
    print("❄️  SnowIO: Interactive Landsat Scene Query")
    print("=" * 80)
    print()
    print("This tool allows you to:")
    print("  • Draw a bounding polygon on an interactive map")
    print("  • Search for Landsat scenes within your area of interest")
    print("  • Filter by date range and cloud cover")
    print("  • View results on the map")
    print()
    print("Note: This standalone version saves the map to an HTML file.")
    print("      For full interactive widgets, use the Jupyter notebook version.")
    print()
    
    # Create the query map
    query_map = InteractiveQueryMap()
    map_obj = query_map.create_map()
    
    # Save map to temporary HTML file
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, 'snowio_interactive_map.html')
    
    map_obj.save(html_file)
    
    print(f"✅ Interactive map saved to: {html_file}")
    print()
    print("Instructions:")
    print("  1. The map will open in your default web browser")
    print("  2. Use the drawing tools (□ icon) to draw a polygon")
    print("  3. Export the polygon using the Export button")
    print("  4. Save the polygon.geojson file")
    print("  5. Run the query using the Python API (see example below)")
    print()
    print("Opening map in browser...")
    
    # Open in browser
    webbrowser.open('file://' + html_file)
    
    print()
    print("=" * 80)
    print("Python API Example:")
    print("=" * 80)
    print("""
from snowio import InteractiveQueryMap

# Create query map
qm = InteractiveQueryMap()

# Define your polygon (from exported GeoJSON)
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
    start_date='2023-01-01',
    end_date='2023-12-31',
    username='your_usgs_username',
    password='your_usgs_password',
    dataset='landsat_ot_c2_l2',
    max_cloud_cover=20
)

# Display results
print(f"Found {len(results)} scenes")
for scene in results:
    print(f"  {scene['display_id']} - {scene['acquisition_date']}")

# Export results
qm.export_results('my_scenes.json')
    """)
    print("=" * 80)
    

if __name__ == '__main__':
    main()
