"""
Example: Query Landsat scenes for Denali region during winter months.

This example demonstrates winter snow monitoring use case.
"""

from snowio import InteractiveQueryMap

def main():
    print("=" * 80)
    print("Example: Denali Winter Snow Monitoring")
    print("=" * 80)
    print()
    
    # Create query map instance
    query_map = InteractiveQueryMap()
    
    # Define polygon around Denali, Alaska
    # Coordinates: [longitude, latitude]
    denali_polygon = [
        [-151.5, 63.5],   # Northwest corner
        [-150.0, 63.5],   # Northeast corner
        [-150.0, 62.8],   # Southeast corner
        [-151.5, 62.8],   # Southwest corner
        [-151.5, 63.5]    # Close the polygon
    ]
    
    print("Area of Interest: Denali Region, Alaska")
    print(f"Polygon vertices: {len(denali_polygon)}")
    print()
    
    # Set the polygon
    query_map.set_polygon(denali_polygon)
    
    # Note: To actually run the query, you need valid USGS credentials
    # Uncomment the code below and add your credentials
    
    """
    # Query parameters - winter months
    start_date = '2023-11-01'
    end_date = '2024-03-31'
    max_cloud_cover = 30  # Higher tolerance for winter clouds
    
    print(f"Query Parameters:")
    print(f"  Start Date: {start_date}")
    print(f"  End Date: {end_date}")
    print(f"  Max Cloud Cover: {max_cloud_cover}%")
    print(f"  Note: Higher cloud cover threshold for winter conditions")
    print()
    
    # Query Landsat scenes
    try:
        results = query_map.query_scenes(
            polygon_coords=denali_polygon,
            start_date=start_date,
            end_date=end_date,
            username='your_username',
            password='your_password',
            dataset='landsat_ot_c2_l2',
            max_cloud_cover=max_cloud_cover
        )
        
        # Display results
        print(f"✅ Found {len(results)} scenes")
        print()
        
        if results:
            print("Winter scenes:")
            for i, scene in enumerate(results[:10], 1):
                print(f"  {i}. {scene['display_id']}")
                print(f"     Date: {scene['acquisition_date']}")
                print(f"     Cloud Cover: {scene['cloud_cover']}%")
                print()
            
            # Export results
            output_file = 'denali_winter_scenes.json'
            query_map.export_results(output_file)
            print(f"✅ Results exported to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Note: You need valid USGS EarthExplorer credentials.")
    """
    
    print()
    print("To run this query:")
    print("1. Register for a free USGS EarthExplorer account")
    print("2. Uncomment the query code in this file")
    print("3. Add your credentials")
    print("4. Run the script")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
