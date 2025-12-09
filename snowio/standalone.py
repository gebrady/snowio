#!/usr/bin/env python3
"""
Standalone script for interactive Landsat scene query.
This version can be run outside of Jupyter notebooks.
"""

from snowio import InteractiveQueryMap
import webbrowser
import os
import tempfile
import sys


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
    
    # Create the query map
    query_map = InteractiveQueryMap()
    
    # Check if user wants to query with an existing polygon
    if len(sys.argv) > 1 and sys.argv[1] == 'query':
        print("Query mode: Using saved polygon to search for scenes")
        print()
        run_query(query_map)
    else:
        print("Map mode: Draw and export polygon")
        print()
        show_map(query_map)


def show_map(query_map):
    """Display the map for polygon drawing."""
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
    print("  3. Click the 'Export' button (top right) to download")
    print("  4. Save as 'polygon.geojson' in your current directory")
    print("  5. Run: python -m snowio.standalone query")
    print()
    print("Opening map in browser...")
    
    # Open in browser
    webbrowser.open('file://' + html_file)
    
    print()
    print("After drawing and exporting your polygon, run:")
    print("  python -m snowio.standalone query")
    print()


def run_query(query_map):
    """Run query using saved polygon."""
    # Look for polygon file
    polygon_file = 'polygon.geojson'
    if not os.path.exists(polygon_file):
        print(f"❌ Error: {polygon_file} not found")
        print()
        print("Please draw and export a polygon first:")
        print("  python -m snowio.standalone")
        print()
        return
    
    # Load the polygon
    try:
        query_map.load_polygon_from_geojson(polygon_file)
    except Exception as e:
        print(f"❌ Error loading polygon: {e}")
        return
    
    # Get query parameters from user
    print()
    print("Enter query parameters:")
    print()
    
    start_date = input("Start date (YYYY-MM-DD) [2023-06-01]: ").strip() or "2023-06-01"
    end_date = input("End date (YYYY-MM-DD) [2023-08-31]: ").strip() or "2023-08-31"
    
    try:
        max_cloud = int(input("Max cloud cover % [20]: ").strip() or "20")
    except ValueError:
        max_cloud = 20
    
    print()
    print("Dataset options:")
    print("  1. Landsat 8 Collection 2 Level 1")
    print("  2. Landsat 8 Collection 2 Level 2 (recommended)")
    print("  3. Landsat 9 Collection 2 Level 1")
    print("  4. Landsat 9 Collection 2 Level 2 (recommended)")
    
    dataset_choice = input("Select dataset [2]: ").strip() or "2"
    dataset_map = {
        "1": "landsat_ot_c2_l1",
        "2": "landsat_ot_c2_l2",
        "3": "landsat_ot_c2_l1",
        "4": "landsat_ot_c2_l2"
    }
    dataset = dataset_map.get(dataset_choice, "landsat_ot_c2_l2")
    
    print()
    username = input("USGS Username: ").strip()
    if not username:
        print("❌ Username required")
        return
    
    import getpass
    password = getpass.getpass("USGS Password: ")
    if not password:
        print("❌ Password required")
        return
    
    # Run the query
    print()
    print("🔍 Searching for Landsat scenes...")
    print(f"   Date range: {start_date} to {end_date}")
    print(f"   Max cloud cover: {max_cloud}%")
    print(f"   Dataset: {dataset}")
    print()
    
    try:
        results = query_map.query_scenes(
            polygon_coords=query_map.drawn_polygon,
            start_date=start_date,
            end_date=end_date,
            username=username,
            password=password,
            dataset=dataset,
            max_cloud_cover=max_cloud
        )
        
        query_map.results = results
        
        # Display results
        if results:
            print(f"✅ Found {len(results)} scenes")
            print()
            print("=" * 100)
            print(f"{'Scene ID':<45} {'Date':<15} {'Cloud Cover':<15} {'Path/Row':<15}")
            print("=" * 100)
            
            for scene in results[:10]:  # Show first 10
                scene_id = scene.get('display_id', scene.get('entityId', 'N/A'))
                date = scene.get('acquisition_date', scene.get('temporal_coverage', 'N/A'))
                cloud_cover = scene.get('cloud_cover', 'N/A')
                if isinstance(cloud_cover, (int, float)):
                    cloud_cover = f"{cloud_cover:.1f}%"
                
                path = scene.get('wrs_path', 'N/A')
                row = scene.get('wrs_row', 'N/A')
                path_row = f"{path}/{row}"
                
                print(f"{scene_id:<45} {str(date):<15} {str(cloud_cover):<15} {path_row:<15}")
            
            if len(results) > 10:
                print(f"... and {len(results) - 10} more scenes")
            print("=" * 100)
            
            # Export results
            output_file = 'landsat_scenes.json'
            query_map.export_results(output_file)
            print()
            print(f"💾 Full results exported to: {output_file}")
        else:
            print("ℹ️  No scenes found matching the criteria.")
            print("   Try expanding your date range or increasing cloud cover threshold.")
        
    except Exception as e:
        print(f"❌ Error during query: {str(e)}")
        print()
        print("Common issues:")
        print("  • Invalid USGS credentials")
        print("  • Network connection problems")
        print("  • API service unavailable")
        print()
        print("Register for free at: https://ers.cr.usgs.gov/register")


if __name__ == '__main__':
    main()
