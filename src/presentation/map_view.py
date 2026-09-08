import tkinter as tk


class MapView:
    def __init__(self, parent):
        self.widget = None
        try:
            import tkintermapview
            self.widget = tkintermapview.TkinterMapView(parent, corner_radius=0)
            self.widget.pack(fill="both", expand=True)
        except ImportError:
            self.widget = tk.Label(parent, text="Map display dependency is not installed", anchor="center")
            self.widget.pack(fill="both", expand=True)

    def set_click_callback(self, callback):
        """Register a callback receiving latitude and longitude from map clicks."""
        if hasattr(self.widget, "add_left_click_map_command"):
            self.widget.add_left_click_map_command(callback)

    def show_points(self, locations):
        """Display markers linked in their current order, without an optimized route."""
        if not hasattr(self.widget, "set_marker"):
            return
        self.clear_route()
        coordinates = []
        for location in locations:
            self.widget.set_marker(location.latitude, location.longitude, text=location.label)
            coordinates.append((location.latitude, location.longitude))
        if len(coordinates) >= 2:
            self.widget.set_path(coordinates)
        self._fit(coordinates)

    def show_result(self, locations, geometry=()):
        if not hasattr(self.widget, "set_marker"):
            return
        self.clear_route()
        for location in locations:
            self.widget.set_marker(location.latitude, location.longitude, text=location.label)
        point_coordinates = [
            (location.latitude, location.longitude) for location in locations
        ]
        route_coordinates = list(geometry) or point_coordinates
        if len(route_coordinates) >= 2:
            self.widget.set_path(route_coordinates)
        self._fit(route_coordinates or point_coordinates)

    def _fit(self, coordinates):
        if not coordinates or not hasattr(self.widget, "fit_bounding_box"):
            return
        latitudes = [latitude for latitude, _ in coordinates]
        longitudes = [longitude for _, longitude in coordinates]
        if len(coordinates) == 1 and hasattr(self.widget, "set_position"):
            self.widget.set_position(latitudes[0], longitudes[0])
            return
        self.widget.fit_bounding_box(
            (max(latitudes), min(longitudes)),
            (min(latitudes), max(longitudes)),
        )

    def clear_route(self):
        if hasattr(self.widget, "delete_all_marker"):
            self.widget.delete_all_marker()
        if hasattr(self.widget, "delete_all_path"):
            self.widget.delete_all_path()
