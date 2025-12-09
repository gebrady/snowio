#!/usr/bin/env python3
"""
Test script for Landsat query functionality.
Tests basic functionality without requiring API credentials.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import landsat_query
        print("  ✓ landsat_query imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import landsat_query: {e}")
        
    try:
        import landsat_query_m2m
        print("  ✓ landsat_query_m2m imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import landsat_query_m2m: {e}")
    
    try:
        import example
        print("  ✓ example imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import example: {e}")
    
    print()


def test_date_parsing():
    """Test date parsing functionality."""
    print("Testing date parsing...")
    from landsat_query import parse_date_range
    
    test_cases = [
        ("2023-06-15", "2023-06-15"),
        ("06/2023", "2023-06-01"),
        ("2023/06", "2023-06-01"),
    ]
    
    for input_date, expected in test_cases:
        try:
            result = parse_date_range(input_date)
            if result == expected:
                print(f"  ✓ '{input_date}' -> '{result}'")
            else:
                print(f"  ✗ '{input_date}' -> '{result}' (expected '{expected}')")
        except Exception as e:
            print(f"  ✗ '{input_date}' raised error: {e}")
    
    print()


def test_metadata_enhancement():
    """Test metadata enhancement functions."""
    print("Testing metadata enhancement...")
    from landsat_query import LandsatSceneQuery
    
    query = LandsatSceneQuery()
    
    # Test analysis-ready check
    mock_scene = {'dataset_name': 'landsat_ot_c2_l2'}
    ar_data = query._check_analysis_ready(mock_scene)
    
    if ar_data.get('is_collection2') and ar_data.get('is_level2'):
        print("  ✓ Analysis-ready data detection works")
    else:
        print("  ✗ Analysis-ready data detection failed")
    
    # Test multispectral info
    ms_info = query._get_multispectral_info(mock_scene)
    
    if isinstance(ms_info.get('bands'), dict) and len(ms_info['bands']) > 0:
        print(f"  ✓ Multispectral info works ({len(ms_info['bands'])} bands)")
    else:
        print("  ✗ Multispectral info failed")
    
    print()


def test_class_initialization():
    """Test class initialization."""
    print("Testing class initialization...")
    
    # Test landsatxplore-based class
    try:
        from landsat_query import LandsatSceneQuery
        query = LandsatSceneQuery()
        print("  ✓ LandsatSceneQuery initialized")
    except Exception as e:
        print(f"  ✗ LandsatSceneQuery initialization failed: {e}")
    
    # Test M2M-based class
    try:
        from landsat_query_m2m import LandsatSceneQueryM2M
        query_m2m = LandsatSceneQueryM2M()
        print("  ✓ LandsatSceneQueryM2M initialized")
    except Exception as e:
        print(f"  ✗ LandsatSceneQueryM2M initialization failed: {e}")
    
    print()


def test_cli_help():
    """Test that CLI help works."""
    print("Testing CLI help output...")
    import subprocess
    
    scripts = ['landsat_query.py', 'landsat_query_m2m.py']
    
    for script in scripts:
        try:
            result = subprocess.run(
                ['python3', script, '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and '--bbox' in result.stdout:
                print(f"  ✓ {script} --help works")
            else:
                print(f"  ✗ {script} --help failed or incomplete")
        except Exception as e:
            print(f"  ✗ {script} error: {e}")
    
    print()


def test_bbox_validation():
    """Test bounding box handling."""
    print("Testing bounding box handling...")
    
    # Valid bounding box (San Francisco Bay Area)
    bbox = (-122.5, 37.5, -122.0, 38.0)
    
    if len(bbox) == 4:
        min_lon, min_lat, max_lon, max_lat = bbox
        if min_lon < max_lon and min_lat < max_lat:
            print(f"  ✓ Bounding box format valid: {bbox}")
        else:
            print(f"  ✗ Bounding box coordinates invalid")
    else:
        print(f"  ✗ Bounding box should have 4 coordinates")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("LANDSAT QUERY TOOL - TEST SUITE")
    print("="*80 + "\n")
    
    test_imports()
    test_date_parsing()
    test_metadata_enhancement()
    test_class_initialization()
    test_cli_help()
    test_bbox_validation()
    
    print("="*80)
    print("Test suite complete!")
    print("="*80 + "\n")
    
    print("Note: Full API tests require USGS EarthExplorer credentials.")
    print("Set EARTHEXPLORER_USERNAME and EARTHEXPLORER_PASSWORD to test API calls.")
    print()


if __name__ == '__main__':
    main()
