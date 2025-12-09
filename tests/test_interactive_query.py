"""
Test suite for SnowIO interactive query functionality.
"""

import unittest
import tempfile
import json
import os
from snowio import InteractiveQueryMap


class TestInteractiveQueryMap(unittest.TestCase):
    """Test cases for InteractiveQueryMap class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.query_map = InteractiveQueryMap()
    
    def test_initialization(self):
        """Test that InteractiveQueryMap initializes correctly."""
        self.assertIsNone(self.query_map.map)
        self.assertIsNone(self.query_map.drawn_polygon)
        self.assertEqual(self.query_map.results, [])
    
    def test_create_map(self):
        """Test that create_map returns a Folium map object."""
        map_obj = self.query_map.create_map()
        self.assertIsNotNone(map_obj)
        self.assertIsNotNone(self.query_map.map)
    
    def test_set_polygon_valid(self):
        """Test setting a valid polygon."""
        polygon = [
            [-150.5, 61.5],
            [-149.0, 61.5],
            [-149.0, 60.8],
            [-150.5, 60.8],
            [-150.5, 61.5]
        ]
        self.query_map.set_polygon(polygon)
        self.assertEqual(self.query_map.drawn_polygon, polygon)
    
    def test_set_polygon_too_many_vertices(self):
        """Test that polygon with > 100 vertices raises ValueError."""
        # Create a polygon with 101 vertices
        polygon = [[i, i] for i in range(101)]
        
        with self.assertRaises(ValueError) as context:
            self.query_map.set_polygon(polygon)
        
        self.assertIn("100 vertices", str(context.exception))
    
    def test_set_polygon_max_vertices(self):
        """Test that polygon with exactly 100 vertices is accepted."""
        # Create a polygon with exactly 100 vertices
        polygon = [[i, i] for i in range(100)]
        
        # Should not raise an exception
        self.query_map.set_polygon(polygon)
        self.assertEqual(len(self.query_map.drawn_polygon), 100)
    
    def test_alaska_center_coordinates(self):
        """Test that Alaska center coordinates are correct."""
        self.assertEqual(self.query_map.ALASKA_CENTER, [64.0, -152.0])
        self.assertEqual(self.query_map.ALASKA_ZOOM, 4)
    
    def test_export_results_no_results(self):
        """Test export_results when no results exist."""
        # Should handle gracefully without crashing
        self.query_map.export_results('test_output.json')
    
    def test_create_widgets(self):
        """Test that create_widgets returns a widget container."""
        widgets_box = self.query_map.create_widgets()
        self.assertIsNotNone(widgets_box)
    
    def test_load_polygon_from_geojson(self):
        """Test loading polygon from GeoJSON file."""
        # Create a temporary GeoJSON file
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-150.5, 61.5],
                                [-149.0, 61.5],
                                [-149.0, 60.8],
                                [-150.5, 60.8],
                                [-150.5, 61.5]
                            ]
                        ]
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as f:
            json.dump(geojson_data, f)
            temp_file = f.name
        
        try:
            self.query_map.load_polygon_from_geojson(temp_file)
            self.assertEqual(len(self.query_map.drawn_polygon), 5)
            self.assertEqual(self.query_map.drawn_polygon[0], [-150.5, 61.5])
        finally:
            os.unlink(temp_file)
    
    def test_load_polygon_from_geojson_invalid_file(self):
        """Test loading polygon from non-existent file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.query_map.load_polygon_from_geojson('nonexistent.geojson')
    
    def test_load_polygon_too_many_vertices_from_geojson(self):
        """Test that loading polygon with >100 vertices from GeoJSON raises error."""
        # Create GeoJSON with 101 vertices
        coords = [[i, i] for i in range(101)]
        coords.append(coords[0])  # Close the polygon
        
        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as f:
            json.dump(geojson_data, f)
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.query_map.load_polygon_from_geojson(temp_file)
            self.assertIn("102 vertices", str(context.exception))
        finally:
            os.unlink(temp_file)
    

class TestPolygonValidation(unittest.TestCase):
    """Test polygon validation logic."""
    
    def test_valid_triangle(self):
        """Test a simple valid triangle polygon."""
        query_map = InteractiveQueryMap()
        triangle = [
            [-150.0, 61.0],
            [-149.5, 61.0],
            [-149.75, 61.5],
            [-150.0, 61.0]
        ]
        query_map.set_polygon(triangle)
        self.assertEqual(len(query_map.drawn_polygon), 4)
    
    def test_valid_complex_polygon(self):
        """Test a more complex polygon with many vertices."""
        query_map = InteractiveQueryMap()
        # Create a polygon with 50 vertices
        polygon = [[i * 0.1, i * 0.1] for i in range(50)]
        query_map.set_polygon(polygon)
        self.assertEqual(len(query_map.drawn_polygon), 50)


if __name__ == '__main__':
    unittest.main()
