# SnowIO Architecture and Implementation

## Overview

SnowIO is an interactive tool for querying Landsat satellite scenes based on user-drawn polygons and temporal ranges. It combines web-based mapping (Folium/Leaflet), interactive widgets (ipywidgets), and satellite data APIs (landsatxplore) to provide a comprehensive query interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Jupyter Notebook  │  Standalone Script  │  Python API     │
├─────────────────────────────────────────────────────────────┤
│                  InteractiveQueryMap Class                  │
│  - Map creation    │  - Widget management │  - Query logic  │
├─────────────────────────────────────────────────────────────┤
│                    Library Layer                             │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Folium     │  ipywidgets  │   Shapely    │ landsatxplore │
│  (Mapping)   │   (UI)       │  (Geometry)  │  (Data API)   │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## Core Components

### 1. InteractiveQueryMap Class

**Location:** `snowio/interactive_query.py`

**Responsibilities:**
- Map creation and configuration
- Widget generation and management
- Polygon validation and storage
- Landsat scene querying
- Result display and export

**Key Methods:**

```python
create_map()              # Initialize Folium map with layers
create_widgets()          # Generate ipywidget controls
set_polygon(coords)       # Set AOI polygon (max 100 vertices)
query_scenes(...)         # Query Landsat scenes via API
display()                 # Show map and widgets in Jupyter
export_results(filename)  # Export results to JSON
```

### 2. Map Configuration

**Default Settings:**
- Center: 64.0°N, 152.0°W (Alaska)
- Zoom: 4 (state-level view)
- Projection: Web Mercator (EPSG:3857)

**Basemap Layers:**
1. OpenStreetMap - Streets and place names
2. ESRI World Imagery - RGB satellite imagery
3. ESRI Shaded Relief - Topographic relief

**Drawing Tools:**
- Polygon drawing (max 100 vertices)
- Rectangle drawing
- Shape editing and deletion
- GeoJSON export

**Additional Plugins:**
- Fullscreen control
- Mouse position display
- Distance/area measurement
- Layer control

### 3. Query System

**Data Source:** USGS EarthExplorer via landsatxplore library

**Query Parameters:**
- Bounding box (from polygon)
- Date range (YYYY-MM-DD)
- Cloud cover threshold (0-100%)
- Dataset selection (Landsat 8/9, Level 1/2)

**Query Workflow:**
```
User Input → Polygon Validation → Bounding Box Creation →
API Authentication → Scene Search → Result Filtering →
Display/Export
```

**Result Fields:**
- display_id: Scene identifier
- acquisition_date: Image capture date
- cloud_cover: Cloud cover percentage
- wrs_path/wrs_row: Landsat path/row
- latitude/longitude: Scene center coordinates

### 4. Widget System

**Interactive Controls:**
- DatePicker (start/end dates)
- IntSlider (cloud cover threshold)
- Dropdown (dataset selection)
- Text/Password (USGS credentials)
- Button (search trigger)
- Output (results display)

**Layout:**
```
VBox (Main Container)
├── HTML (Instructions)
├── HBox (Date Range)
│   ├── DatePicker (Start)
│   └── DatePicker (End)
├── VBox (Parameters)
│   ├── IntSlider (Cloud Cover)
│   └── Dropdown (Dataset)
├── VBox (Credentials)
│   ├── Text (Username)
│   └── Password (Password)
├── Button (Search)
└── Output (Results)
```

## Data Flow

### Map Interaction Flow
```
User draws polygon on map
    ↓
JavaScript captures coordinates
    ↓
Python receives GeoJSON
    ↓
Shapely validates geometry
    ↓
Coordinates stored in query_map.drawn_polygon
```

### Query Flow
```
User clicks "Search Scenes"
    ↓
Validate inputs (polygon, dates, credentials)
    ↓
Create bounding box from polygon
    ↓
Authenticate with USGS API
    ↓
Submit search request
    ↓
Receive scene metadata
    ↓
Filter by polygon intersection
    ↓
Display results in table
    ↓
Store in query_map.results
    ↓
User exports to JSON
```

## File Structure

```
snowio/
├── snowio/                      # Main package
│   ├── __init__.py             # Package initialization
│   ├── interactive_query.py    # Core InteractiveQueryMap class
│   └── standalone.py           # Standalone script runner
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_interactive_query.py
├── examples/                    # Example scripts
│   ├── query_anchorage.py
│   └── query_denali_winter.py
├── interactive_query.ipynb     # Jupyter notebook interface
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── README.md                   # Main documentation
├── QUICKSTART.md              # Quick start guide
├── VISUAL_GUIDE.md            # Visual interface guide
└── .gitignore                 # Git ignore rules
```

## Dependencies

### Core Libraries
- **folium** (≥0.14.0): Interactive mapping (Leaflet.js wrapper)
- **ipywidgets** (≥8.0.0): Jupyter interactive widgets
- **shapely** (≥2.0.0): Geometric operations
- **landsatxplore** (≥0.14.0): USGS Landsat API client

### Supporting Libraries
- **jupyter** (≥1.0.0): Notebook environment
- **ipykernel** (≥6.0.0): Python kernel for Jupyter
- **requests** (≥2.28.0): HTTP library

## Design Decisions

### 1. Folium for Mapping
**Rationale:** 
- Pure Python (no JavaScript needed)
- Rich plugin ecosystem
- Easy integration with Jupyter
- Generates standalone HTML

**Alternatives Considered:**
- ipyleaflet: More Jupyter-native but less standalone
- Plotly: Good for data viz but limited mapping features
- Bokeh: Powerful but steeper learning curve

### 2. landsatxplore for Data Access
**Rationale:**
- Simple Python API
- Handles authentication
- Supports multiple Landsat collections
- Active maintenance

**Alternatives Considered:**
- sat-search: Good but deprecated
- sentinelsat: Sentinel-focused
- Direct USGS API: Too low-level

### 3. ipywidgets for UI
**Rationale:**
- Native Jupyter integration
- Rich widget set
- Event-driven architecture
- Easy to customize

**Alternatives Considered:**
- Panel: More powerful but heavier
- Voila: Requires separate server
- Streamlit: Not Jupyter-native

### 4. 100-Vertex Limit
**Rationale:**
- Prevents performance issues
- Matches typical use cases
- Simplifies validation
- Aligns with API limits

## Security Considerations

### Credential Handling
- Passwords stored in Password widget (not plain text)
- Credentials never logged or exported
- API sessions properly closed after use
- No credential caching

### Input Validation
- Polygon vertex count checked
- Coordinate format validated
- Date range validation
- SQL injection prevention (API handles)

## Performance Optimization

### Map Rendering
- Lazy loading of tile layers
- Viewport-based tile fetching
- Efficient GeoJSON handling

### Query Optimization
- Bounding box pre-filtering
- Maximum result limit (100 scenes)
- Async API operations
- Connection pooling

## Testing Strategy

### Unit Tests
- Polygon validation (max vertices)
- Map initialization
- Widget creation
- Coordinate handling

### Integration Tests
- Map layer rendering
- Widget interaction
- Export functionality

### Manual Tests
- Browser compatibility
- Jupyter notebook display
- Credential authentication
- Result accuracy

## Future Enhancements

### Potential Additions
1. **Multiple polygon support** - Query multiple AOIs
2. **Scene preview** - Thumbnail display in results
3. **Download integration** - Direct scene download
4. **Temporal animation** - Animate scene time series
5. **Advanced filtering** - Solar angle, sensor quality
6. **Cloud detection** - Refined cloud masking
7. **Result caching** - Store previous queries
8. **Batch export** - Export multiple formats

### API Improvements
1. **Retry logic** - Handle API failures
2. **Rate limiting** - Respect API quotas
3. **Progress tracking** - Show query progress
4. **Parallel queries** - Multiple simultaneous requests

## Troubleshooting

### Common Issues

**Issue:** Map not displaying in Jupyter
**Cause:** Widget extensions not enabled
**Fix:** `jupyter nbextension enable --py widgetsnbextension`

**Issue:** Import error for landsatxplore
**Cause:** Dependency not installed
**Fix:** `pip install landsatxplore`

**Issue:** Authentication failure
**Cause:** Invalid credentials or inactive account
**Fix:** Verify account at https://ers.cr.usgs.gov

**Issue:** No results returned
**Cause:** Query parameters too restrictive
**Fix:** Expand date range or increase cloud cover threshold

## Development Guidelines

### Code Style
- PEP 8 compliance
- Type hints where appropriate
- Comprehensive docstrings
- Clear variable naming

### Git Workflow
- Feature branches for new development
- Descriptive commit messages
- Pull request reviews
- Issue tracking

### Documentation
- Code comments for complex logic
- API documentation in docstrings
- User guides for features
- Example scripts for common use cases

## References

- Folium Documentation: https://python-visualization.github.io/folium/
- Leaflet.js Documentation: https://leafletjs.com/
- ipywidgets Documentation: https://ipywidgets.readthedocs.io/
- USGS EarthExplorer: https://earthexplorer.usgs.gov/
- Landsat Documentation: https://www.usgs.gov/landsat-missions
