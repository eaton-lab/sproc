#!/usr/env/bin python

"""
Draw maps with folium
"""

import os
import folium
import geopandas


# TODO: make MultiIMap object, to compare with original (renamed SingleIMap).


class SingleIMap:
    """
    Parameters:
    ------------
    location: Tuple[Float,Float]
        LatLong Point as center of the map.
    zoom_start: 
    """
    def __init__(self, json_file):
        self.json_file = json_file
        self.name = os.path.basename(self.json_file).rsplit(".json")[0]
        self.data = geopandas.read_file(json_file)
        self.imap = None

        self._get_base_imap()
        self._add_poly()
        self._add_points()
        self._add_outlier_points()
        self.imap.add_child(folium.LayerControl())


    def add_geojson(self, json_file):
        """
        Add GeoJson data from another sproc geojson file to this map.
        This can be used to merge together bounds and points from two
        or more species.
        """
        self.json_file = json_file
        self.name = os.path.basename(self.json_file).rsplit(".json")[0]
        self.data = geopandas.read_file(json_file)

        # self._add_poly()
        self._add_points()
        # self._add_outlier_points()

        # refit the bounds
        # ...


    def _get_base_imap(self):
        """
        Load a basemap 
        """
        # create the baselayer map
        self.imap = folium.Map()
        # tiles='Stamen Terrain'
        # tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png',
        # attr="IGN",


    def _add_poly(self):
        """
        Adds a MultiPolygon for the geographic range on its own layer
        """
        # make a layer for the polygon shape
        layer_poly = folium.FeatureGroup(name=f"{self.name} bounds")
        
        # add the polygon to this layer
        layer_poly.add_child(
            folium.GeoJson(
                data=self.data[self.data['type']=="geographic_range"])
        )

        # add this layer to the map
        self.imap.add_child(layer_poly)
        # self.imap.fit_bounds(layer_poly.get_bounds())


    def _add_points(self):
        """
        Adds markers for occurrence points on a separate layer
        """
        # make a layer for points
        layer_points = folium.FeatureGroup(name=f"{self.name} occurrence")

        # get points as markers
        mask1 = self.data['type'] == "occurrence"
        mask2 = self.data['outlier'] == 'false'
        markers = folium.GeoJson(
            data=self.data[mask1 & mask2],
            popup=folium.GeoJsonPopup(fields=("record",), aliases=("",)),
        )

        # add markers to layer
        layer_points.add_child(markers)
        
        # add this layer to the map
        self.imap.add_child(layer_points)


    def _add_outlier_points(self):
        """
        Adds outliers as Points in red color
        """
        # skip if no outliers present
        if all(self.data[self.data['type'] == 'occurrence'].outlier == "false"):
            return 

        # make a layer for points
        layer_outliers = folium.FeatureGroup(name="Outliers")

        # get points as markers
        mask1 = self.data['type'] == "occurrence"
        mask2 = self.data['outlier'] == 'true'
        markers = folium.GeoJson(
            data=self.data[mask1 & mask2],
            popup=folium.GeoJsonPopup(fields=("record",), aliases=("",)),
            marker=folium.Marker(
                icon=folium.Icon(color="red", icon="trash")
            )
        )

        # add markers to layer
        layer_outliers.add_child(markers)
        
        # add this layer to the map
        self.imap.add_child(layer_outliers)
