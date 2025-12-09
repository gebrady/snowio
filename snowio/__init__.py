"""
snowio - Landsat snow analysis toolkit
"""

__version__ = "0.1.0"

from .ndsi import calculate_ndsi, process_scene
from .utils import identify_landsat_version, crop_to_aoi, classify_snow_glacier

__all__ = [
    "calculate_ndsi",
    "process_scene",
    "identify_landsat_version",
    "crop_to_aoi",
    "classify_snow_glacier",
]
