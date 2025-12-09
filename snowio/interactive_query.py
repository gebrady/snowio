"""
Interactive query map for finding Landsat scenes based on user-drawn polygons
and date ranges. Uses Folium for interactive mapping with OSM and imagery layers.
"""

import folium
from folium import plugins
import ipywidgets as widgets
from IPython.display import display, HTML
from datetime import datetime, timedelta
import json
from shapely.geometry import Polygon

# Optional imports for Landsat querying
try:
    from landsatxplore.api import API
    from landsatxplore.earthexplorer import EarthExplorer
    LANDSAT_AVAILABLE = True
except ImportError:
    LANDSAT_AVAILABLE = False
    print("Warning: landsatxplore not available. Install with: pip install landsatxplore")


class InteractiveQueryMap:
    """
    Interactive map for querying Landsat scenes based on user-drawn polygons.
    
    Features:
    - Interactive map centered on Alaska
    - Multiple basemap layers (OSM, RGB imagery, shaded relief)
    - Draw polygon tool (max 100 vertices)
    - Date range input
    - Landsat scene search
    """
    
    # Alaska center coordinates
    ALASKA_CENTER = [64.0, -152.0]
    ALASKA_ZOOM = 4
    
    def __init__(self):
        """Initialize the interactive query map."""
        self.map = None
        self.drawn_polygon = None
        self.date_start = None
        self.date_end = None
        self.results = []
        self.username = None
        self.password = None
        
    def create_map(self):
        """
        Create the interactive Folium map with multiple layers.
        
        Returns:
            folium.Map: The configured map object
        """
        # Create base map centered on Alaska
        m = folium.Map(
            location=self.ALASKA_CENTER,
            zoom_start=self.ALASKA_ZOOM,
            tiles=None  # We'll add custom tiles
        )
        
        # Add OpenStreetMap base layer with streets and place names
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add ESRI World Imagery (RGB satellite imagery)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='ESRI World Imagery',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add ESRI World Shaded Relief
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Shaded Relief',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add drawing tools for polygon
        draw = plugins.Draw(
            export=True,
            filename='polygon.geojson',
            position='topleft',
            draw_options={
                'polyline': False,
                'polygon': {
                    'allowIntersection': False,
                    'showArea': True,
                    'metric': True,
                    'shapeOptions': {
                        'color': '#3388ff',
                        'fillOpacity': 0.2
                    }
                },
                'circle': False,
                'rectangle': True,
                'marker': False,
                'circlemarker': False
            },
            edit_options={
                'edit': True,
                'remove': True
            }
        )
        draw.add_to(m)
        
        # Add fullscreen button
        plugins.Fullscreen(
            position='topright',
            title='Fullscreen',
            title_cancel='Exit fullscreen',
            force_separate_button=True
        ).add_to(m)
        
        # Add mouse position plugin
        plugins.MousePosition().add_to(m)
        
        # Add measure control
        plugins.MeasureControl(
            position='topleft',
            primary_length_unit='kilometers',
            secondary_length_unit='miles',
            primary_area_unit='sqkilometers',
            secondary_area_unit='acres'
        ).add_to(m)
        
        self.map = m
        return m
    
    def create_widgets(self):
        """
        Create interactive widgets for date input and query controls.
        
        Returns:
            widgets.VBox: Container with all widgets
        """
        # Date range inputs
        today = datetime.now()
        default_start = today - timedelta(days=365)
        
        self.start_date_widget = widgets.DatePicker(
            description='Start Date:',
            value=default_start.date(),
            disabled=False,
            style={'description_width': 'initial'}
        )
        
        self.end_date_widget = widgets.DatePicker(
            description='End Date:',
            value=today.date(),
            disabled=False,
            style={'description_width': 'initial'}
        )
        
        # Cloud cover filter
        self.cloud_cover_widget = widgets.IntSlider(
            value=20,
            min=0,
            max=100,
            step=1,
            description='Max Cloud Cover (%):',
            style={'description_width': 'initial'},
            continuous_update=False
        )
        
        # Dataset selection
        # Note: Landsat 8 and 9 share the same dataset identifiers in Collection 2
        # The API automatically includes both satellites when querying these datasets
        self.dataset_widget = widgets.Dropdown(
            options=[
                ('Landsat 8 Collection 2 Level 1', 'landsat_ot_c2_l1'),
                ('Landsat 8 Collection 2 Level 2', 'landsat_ot_c2_l2'),
                ('Landsat 9 Collection 2 Level 1', 'landsat_ot_c2_l1'),
                ('Landsat 9 Collection 2 Level 2', 'landsat_ot_c2_l2')
            ],
            value='landsat_ot_c2_l2',
            description='Dataset:',
            style={'description_width': 'initial'}
        )
        
        # Credentials (stored in widgets but not displayed in plain text)
        self.username_widget = widgets.Text(
            description='USGS Username:',
            placeholder='Enter USGS EarthExplorer username',
            style={'description_width': 'initial'}
        )
        
        self.password_widget = widgets.Password(
            description='USGS Password:',
            placeholder='Enter USGS EarthExplorer password',
            style={'description_width': 'initial'}
        )
        
        # Query button
        self.query_button = widgets.Button(
            description='Search Scenes',
            button_style='primary',
            tooltip='Search for Landsat scenes',
            icon='search'
        )
        self.query_button.on_click(self._on_query_click)
        
        # Output area for results
        self.output = widgets.Output()
        
        # Info text
        info_html = widgets.HTML(
            value="""
            <div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin: 10px 0;">
                <h3>Instructions:</h3>
                <ol>
                    <li>Draw a polygon on the map using the drawing tools (square icon on the left)</li>
                    <li>Limit your polygon to a maximum of 100 vertices</li>
                    <li>Select date range for scene search</li>
                    <li>Enter USGS EarthExplorer credentials (register at <a href="https://ers.cr.usgs.gov/register" target="_blank">USGS</a>)</li>
                    <li>Click "Search Scenes" to query Landsat data</li>
                </ol>
                <p><strong>Note:</strong> You need a free USGS EarthExplorer account to query Landsat data.</p>
            </div>
            """
        )
        
        # Arrange widgets
        date_box = widgets.HBox([self.start_date_widget, self.end_date_widget])
        params_box = widgets.VBox([
            self.cloud_cover_widget,
            self.dataset_widget
        ])
        creds_box = widgets.VBox([
            self.username_widget,
            self.password_widget
        ])
        
        return widgets.VBox([
            info_html,
            widgets.HTML('<h4>Search Parameters:</h4>'),
            date_box,
            params_box,
            widgets.HTML('<h4>USGS Credentials:</h4>'),
            creds_box,
            self.query_button,
            self.output
        ])
    
    def _extract_polygon_from_map(self):
        """
        Extract polygon coordinates from the Folium map.
        Note: In a Jupyter notebook environment, this would be done through
        JavaScript interaction. For this implementation, we provide a method
        to manually set the polygon.
        
        Returns:
            list: Polygon coordinates [[lon, lat], ...]
        """
        return self.drawn_polygon
    
    def set_polygon(self, coordinates):
        """
        Manually set polygon coordinates.
        
        Args:
            coordinates: List of [lon, lat] coordinate pairs, max 100 vertices
        
        Raises:
            ValueError: If coordinates exceed 100 vertices
        """
        if len(coordinates) > 100:
            raise ValueError("Polygon cannot exceed 100 vertices")
        
        self.drawn_polygon = coordinates
    
    def _on_query_click(self, button):
        """Handle query button click."""
        with self.output:
            self.output.clear_output()
            
            # Validate inputs
            if not self.drawn_polygon:
                print("❌ Error: Please draw a polygon on the map first.")
                print("   Use the drawing tools to define your area of interest.")
                return
            
            if not self.username_widget.value or not self.password_widget.value:
                print("❌ Error: Please provide USGS EarthExplorer credentials.")
                print("   Register for free at: https://ers.cr.usgs.gov/register")
                return
            
            # Perform query
            print("🔍 Searching for Landsat scenes...")
            print(f"   Date range: {self.start_date_widget.value} to {self.end_date_widget.value}")
            print(f"   Max cloud cover: {self.cloud_cover_widget.value}%")
            # Get the label (text) corresponding to the current value
            dataset_label = next(label for label, val in self.dataset_widget.options if val == self.dataset_widget.value)
            print(f"   Dataset: {dataset_label}")
            print()
            
            try:
                results = self.query_scenes(
                    self.drawn_polygon,
                    self.start_date_widget.value.strftime('%Y-%m-%d'),
                    self.end_date_widget.value.strftime('%Y-%m-%d'),
                    self.username_widget.value,
                    self.password_widget.value,
                    self.dataset_widget.value,
                    self.cloud_cover_widget.value
                )
                
                self.results = results
                self._display_results(results)
                
            except Exception as e:
                print(f"❌ Error during query: {str(e)}")
                print("   Please check your credentials and try again.")
    
    def query_scenes(self, polygon_coords, start_date, end_date, 
                     username, password, dataset='landsat_ot_c2_l2', 
                     max_cloud_cover=20):
        """
        Query Landsat scenes based on polygon and date range.
        
        Args:
            polygon_coords: List of [lon, lat] coordinate pairs
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            username: USGS EarthExplorer username
            password: USGS EarthExplorer password
            dataset: Landsat dataset identifier
            max_cloud_cover: Maximum cloud cover percentage
        
        Returns:
            list: List of scene metadata dictionaries
        """
        if not LANDSAT_AVAILABLE:
            raise ImportError(
                "landsatxplore is not installed. "
                "Install it with: pip install landsatxplore"
            )
        
        # Create a bounding box from polygon
        lons = [coord[0] for coord in polygon_coords]
        lats = [coord[1] for coord in polygon_coords]
        bbox = (min(lons), min(lats), max(lons), max(lats))
        
        # Initialize API
        api = API(username, password)
        
        try:
            # Search for scenes
            scenes = api.search(
                dataset=dataset,
                bbox=bbox,
                start_date=start_date,
                end_date=end_date,
                max_cloud_cover=max_cloud_cover,
                max_results=100
            )
            
            # Filter scenes by polygon (more precise than bbox)
            polygon = Polygon([(coord[0], coord[1]) for coord in polygon_coords])
            filtered_scenes = []
            
            for scene in scenes:
                # Check if scene intersects with polygon
                # Scene spatial footprint would need to be checked here
                # For simplicity, we include all scenes within bbox
                filtered_scenes.append(scene)
            
            return filtered_scenes
            
        finally:
            api.logout()
    
    def _display_results(self, results):
        """Display query results in a formatted table."""
        if not results:
            print("ℹ️  No scenes found matching the criteria.")
            return
        
        print(f"✅ Found {len(results)} scenes\n")
        print("=" * 100)
        print(f"{'Scene ID':<45} {'Date':<15} {'Cloud Cover':<15} {'Path/Row':<15}")
        print("=" * 100)
        
        for scene in results:
            scene_id = scene.get('display_id', scene.get('entityId', 'N/A'))
            date = scene.get('acquisition_date', scene.get('temporal_coverage', 'N/A'))
            cloud_cover = scene.get('cloud_cover', 'N/A')
            if isinstance(cloud_cover, (int, float)):
                cloud_cover = f"{cloud_cover:.1f}%"
            
            path = scene.get('wrs_path', 'N/A')
            row = scene.get('wrs_row', 'N/A')
            path_row = f"{path}/{row}"
            
            print(f"{scene_id:<45} {str(date):<15} {str(cloud_cover):<15} {path_row:<15}")
        
        print("=" * 100)
    
    def add_results_to_map(self):
        """Add query results as markers on the map."""
        if not self.map or not self.results:
            return
        
        # Create a feature group for results
        results_group = folium.FeatureGroup(name='Search Results')
        
        for scene in self.results:
            # Get scene center coordinates
            lat = scene.get('latitude', None)
            lon = scene.get('longitude', None)
            
            if lat and lon:
                scene_id = scene.get('display_id', scene.get('entityId', 'N/A'))
                date = scene.get('acquisition_date', 'N/A')
                cloud_cover = scene.get('cloud_cover', 'N/A')
                
                popup_html = f"""
                <div style="font-family: Arial; font-size: 12px;">
                    <b>Scene ID:</b> {scene_id}<br>
                    <b>Date:</b> {date}<br>
                    <b>Cloud Cover:</b> {cloud_cover}%<br>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(results_group)
        
        results_group.add_to(self.map)
    
    def display(self):
        """
        Display the interactive map and widgets in a Jupyter notebook.
        
        Returns:
            tuple: (map, widgets) for display
        """
        if not self.map:
            self.create_map()
        
        widgets_box = self.create_widgets()
        
        # Display both
        display(widgets_box)
        display(self.map)
        
        return self.map, widgets_box
    
    def export_results(self, filename='landsat_scenes.json'):
        """
        Export query results to a JSON file.
        
        Args:
            filename: Output filename
        """
        if not self.results:
            print("No results to export.")
            return
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"✅ Exported {len(self.results)} scenes to {filename}")
