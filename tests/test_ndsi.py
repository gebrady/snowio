"""
Tests for snowio package.
"""

import unittest
import numpy as np
from snowio.ndsi import (
    calculate_ndsi,
    identify_landsat_version,
    get_band_numbers,
    classify_snow_glacier
)


class TestNDSI(unittest.TestCase):
    """Test NDSI calculation functions."""
    
    def test_calculate_ndsi_basic(self):
        """Test basic NDSI calculation."""
        green = np.array([[100, 200], [150, 250]], dtype=np.float32)
        swir1 = np.array([[50, 100], [75, 125]], dtype=np.float32)
        
        ndsi = calculate_ndsi(green, swir1)
        
        # NDSI = (Green - SWIR1) / (Green + SWIR1)
        expected = (green - swir1) / (green + swir1)
        np.testing.assert_array_almost_equal(ndsi, expected)
    
    def test_calculate_ndsi_zero_division(self):
        """Test NDSI calculation with zero denominator."""
        green = np.array([[100, 0], [150, 250]], dtype=np.float32)
        swir1 = np.array([[50, 0], [75, 125]], dtype=np.float32)
        
        ndsi = calculate_ndsi(green, swir1)
        
        # Second pixel should be NaN due to zero denominator
        self.assertTrue(np.isnan(ndsi[0, 1]))
        
        # Other pixels should have valid values
        self.assertFalse(np.isnan(ndsi[0, 0]))
        self.assertFalse(np.isnan(ndsi[1, 0]))
        self.assertFalse(np.isnan(ndsi[1, 1]))
    
    def test_calculate_ndsi_range(self):
        """Test that NDSI values are in valid range [-1, 1]."""
        green = np.array([[100, 200, 50]], dtype=np.float32)
        swir1 = np.array([[50, 100, 200]], dtype=np.float32)
        
        ndsi = calculate_ndsi(green, swir1)
        
        # All valid values should be between -1 and 1
        valid_mask = ~np.isnan(ndsi)
        self.assertTrue(np.all(ndsi[valid_mask] >= -1))
        self.assertTrue(np.all(ndsi[valid_mask] <= 1))


class TestLandsatVersion(unittest.TestCase):
    """Test Landsat version identification."""
    
    def test_identify_landsat_8(self):
        """Test identification of Landsat 8."""
        scene = "LC08_L1TP_043034_20201215_20201226_01_T1"
        version = identify_landsat_version(scene)
        self.assertEqual(version, 8)
    
    def test_identify_landsat_9(self):
        """Test identification of Landsat 9."""
        scene = "LC09_L1TP_043034_20211215_20211226_01_T1"
        version = identify_landsat_version(scene)
        self.assertEqual(version, 9)
    
    def test_identify_landsat_7(self):
        """Test identification of Landsat 7."""
        scene = "LE07_L1TP_043034_20101215_20101226_01_T1"
        version = identify_landsat_version(scene)
        self.assertEqual(version, 7)
    
    def test_identify_landsat_5(self):
        """Test identification of Landsat 5."""
        scene = "LT05_L1TP_043034_20001215_20001226_01_T1"
        version = identify_landsat_version(scene)
        self.assertEqual(version, 5)
    
    def test_identify_landsat_4(self):
        """Test identification of Landsat 4."""
        scene = "LT04_L1TP_043034_19901215_19901226_01_T1"
        version = identify_landsat_version(scene)
        self.assertEqual(version, 4)
    
    def test_get_band_numbers_landsat_47(self):
        """Test band numbers for Landsat 4-7."""
        green, swir1 = get_band_numbers(5)
        self.assertEqual(green, 2)
        self.assertEqual(swir1, 5)
        
        green, swir1 = get_band_numbers(7)
        self.assertEqual(green, 2)
        self.assertEqual(swir1, 5)
    
    def test_get_band_numbers_landsat_89(self):
        """Test band numbers for Landsat 8-9."""
        green, swir1 = get_band_numbers(8)
        self.assertEqual(green, 3)
        self.assertEqual(swir1, 6)
        
        green, swir1 = get_band_numbers(9)
        self.assertEqual(green, 3)
        self.assertEqual(swir1, 6)


class TestClassification(unittest.TestCase):
    """Test snow/glacier classification."""
    
    def test_classify_snow_only(self):
        """Test classification without glacier mask."""
        ndsi = np.array([[0.5, 0.3, 0.6],
                        [0.2, 0.7, 0.1],
                        [0.8, 0.35, 0.9]], dtype=np.float32)
        
        classification = classify_snow_glacier(ndsi, glacier_mask=None, ndsi_threshold=0.4)
        
        # Pixels with NDSI >= 0.4 should be class 1 (snow)
        expected = np.array([[1, 0, 1],
                           [0, 1, 0],
                           [1, 0, 1]], dtype=np.uint8)
        
        np.testing.assert_array_equal(classification, expected)
    
    def test_classify_with_glacier_mask(self):
        """Test classification with glacier mask."""
        ndsi = np.array([[0.5, 0.3, 0.6],
                        [0.2, 0.7, 0.1],
                        [0.8, 0.35, 0.9]], dtype=np.float32)
        
        glacier_mask = np.array([[True, False, False],
                                [False, True, False],
                                [True, False, True]], dtype=bool)
        
        classification = classify_snow_glacier(ndsi, glacier_mask=glacier_mask, ndsi_threshold=0.4)
        
        # Pixels with NDSI >= 0.4 and glacier mask should be class 2
        # Other pixels with NDSI >= 0.4 should be class 1
        expected = np.array([[2, 0, 1],
                           [0, 2, 0],
                           [2, 0, 2]], dtype=np.uint8)
        
        np.testing.assert_array_equal(classification, expected)
    
    def test_classify_with_nan(self):
        """Test classification with NaN values."""
        ndsi = np.array([[0.5, np.nan, 0.6],
                        [0.2, 0.7, 0.1]], dtype=np.float32)
        
        classification = classify_snow_glacier(ndsi, glacier_mask=None, ndsi_threshold=0.4)
        
        # NaN pixels should be class 0
        expected = np.array([[1, 0, 1],
                           [0, 1, 0]], dtype=np.uint8)
        
        np.testing.assert_array_equal(classification, expected)
    
    def test_classify_with_separate_thresholds(self):
        """Test classification with separate snow and ice thresholds."""
        ndsi = np.array([[0.5, 0.3, 0.6],
                        [0.2, 0.7, 0.1],
                        [0.8, 0.35, 0.9]], dtype=np.float32)
        
        # Snow threshold: 0.4, Ice threshold: 0.7
        classification = classify_snow_glacier(
            ndsi, 
            glacier_mask=None,
            ndsi_snow_threshold=0.4,
            ndsi_ice_threshold=0.7
        )
        
        # Pixels with NDSI >= 0.7 should be class 2 (ice)
        # Pixels with 0.4 <= NDSI < 0.7 should be class 1 (snow)
        # Pixels with NDSI < 0.4 should be class 0 (unclassified)
        expected = np.array([[1, 0, 1],
                           [0, 2, 0],
                           [2, 0, 2]], dtype=np.uint8)
        
        np.testing.assert_array_equal(classification, expected)
    
    def test_classify_snow_only_with_new_parameter(self):
        """Test classification with only snow threshold (no glacier class)."""
        ndsi = np.array([[0.5, 0.3, 0.6],
                        [0.2, 0.7, 0.1],
                        [0.8, 0.35, 0.9]], dtype=np.float32)
        
        # Only snow threshold provided, no ice threshold
        classification = classify_snow_glacier(
            ndsi, 
            ndsi_snow_threshold=0.4,
            ndsi_ice_threshold=None
        )
        
        # Only classes 0 and 1 should be present (no class 2)
        expected = np.array([[1, 0, 1],
                           [0, 1, 0],
                           [1, 0, 1]], dtype=np.uint8)
        
        np.testing.assert_array_equal(classification, expected)
        # Verify no glacier class (2) is present
        self.assertNotIn(2, classification)
    
    def test_backward_compatibility_with_ndsi_threshold(self):
        """Test backward compatibility using old ndsi_threshold parameter."""
        ndsi = np.array([[0.5, 0.3, 0.6]], dtype=np.float32)
        
        # Using old parameter name
        classification = classify_snow_glacier(ndsi, ndsi_threshold=0.4)
        
        expected = np.array([[1, 0, 1]], dtype=np.uint8)
        np.testing.assert_array_equal(classification, expected)


if __name__ == '__main__':
    unittest.main()
