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
            self.widget.fit_bounding_box(route_coordinates[0], route_coordinates[-1])

    def clear_route(self):
        if hasattr(self.widget, "delete_all_marker"):
            self.widget.delete_all_marker()
        if hasattr(self.widget, "delete_all_path"):
            self.widget.delete_all_path()
