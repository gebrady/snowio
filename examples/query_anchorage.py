"""
Example: Query Landsat scenes for Anchorage area during summer months.

This example demonstrates how to:
1. Define a polygon around Anchorage, Alaska
2. Query for Landsat scenes during summer (June-August)
3. Filter by cloud cover
4. Display and export results
"""

from snowio import InteractiveQueryMap

def main():
    print("=" * 80)
    print("Example: Anchorage Summer Scenes Query")
    print("=" * 80)
    print()
    
    # Create query map instance
    query_map = InteractiveQueryMap()
    
    # Define polygon around Anchorage, Alaska
    # Coordinates: [longitude, latitude]
    anchorage_polygon = [
        [-150.5, 61.5],   # Northwest corner
        [-149.0, 61.5],   # Northeast corner
        [-149.0, 60.8],   # Southeast corner
        [-150.5, 60.8],   # Southwest corner
        [-150.5, 61.5]    # Close the polygon
    ]
    
    print("Area of Interest: Anchorage, Alaska")
    print(f"Polygon vertices: {len(anchorage_polygon)}")
    print()
    
    # Set the polygon
    query_map.set_polygon(anchorage_polygon)
    
    # Note: To actually run the query, you need valid USGS credentials
    # Uncomment the code below and add your credentials
    
    """
    # Query parameters
    start_date = '2023-06-01'
    end_date = '2023-08-31'
    max_cloud_cover = 20
    
    print(f"Query Parameters:")
    print(f"  Start Date: {start_date}")
    print(f"  End Date: {end_date}")
    print(f"  Max Cloud Cover: {max_cloud_cover}%")
    print()
    
    # Query Landsat scenes
    # Replace 'your_username' and 'your_password' with your USGS credentials
    try:
        results = query_map.query_scenes(
            polygon_coords=anchorage_polygon,
            start_date=start_date,
            end_date=end_date,
            username='your_username',
            password='your_password',
            dataset='landsat_ot_c2_l2',  # Landsat 8/9 Collection 2 Level 2
            max_cloud_cover=max_cloud_cover
        )
        
        # Display results
        print(f"✅ Found {len(results)} scenes")
        print()
        
        if results:
            print("Sample scenes:")
            for i, scene in enumerate(results[:5], 1):
                print(f"  {i}. {scene['display_id']}")
                print(f"     Date: {scene['acquisition_date']}")
                print(f"     Cloud Cover: {scene['cloud_cover']}%")
                print(f"     Path/Row: {scene['wrs_path']}/{scene['wrs_row']}")
                print()
            
            # Export results
            output_file = 'anchorage_summer_scenes.json'
            query_map.export_results(output_file)
            print(f"✅ Results exported to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Note: You need valid USGS EarthExplorer credentials to run queries.")
        print("Register at: https://ers.cr.usgs.gov/register")
    """
    
    print()
    print("To run this query:")
    print("1. Register for a free USGS EarthExplorer account")
    print("   https://ers.cr.usgs.gov/register")
    print("2. Uncomment the query code in this file")
    print("3. Replace 'your_username' and 'your_password' with your credentials")
    print("4. Run the script again")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
