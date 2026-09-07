import dataclasses
import threading
import tkinter as tk
import uuid
from tkinter import messagebox, ttk

from src.domain.models import CostCriterion, Journey, Location
from src.presentation.map_view import MapView


class JourneyWindow:
    def __init__(self, root, optimize_service, persistence):
        self.root = root
        self.optimize_service = optimize_service
        self.persistence = persistence
        self.locations: list[Location] = []
        self.current_journey = None
        self.current_result = None
        self.origin_id = None
        self.destination_id = None
        self.label_var = tk.StringVar()
        self.latitude_var = tk.StringVar()
        self.longitude_var = tk.StringVar()
        self.criterion_var = tk.StringVar(value="distance")
        self.distance_weight_var = tk.StringVar(value="0.6")
        self.duration_weight_var = tk.StringVar(value="0.4")
        self.status_var = tk.StringVar(value="Add journey points to begin")
        self.journey_id= tk.StringVar(value="")
        self._build()

    def _build(self):
        self.root.title("Multi-Point Ride Optimizer")
        self.root.geometry("1000x650")
        controls = ttk.Frame(self.root, padding=12)
        controls.pack(side="left", fill="y")
        ttk.Label(controls, text="Journey ID").pack(anchor="w")
        ttk.Label(controls, textvariable=self.journey_id).pack(anchor="w")
        ttk.Label(controls, text="Journey points").pack(anchor="w")
        self.points = tk.Listbox(controls, height=18, width=32)
        self.points.pack()
        self.points.bind("<<ListboxSelect>>", self._on_point_selected)
        for label, variable in (("Label", self.label_var), ("Latitude", self.latitude_var), ("Longitude", self.longitude_var)):
            ttk.Label(controls, text=label).pack(anchor="w", pady=(8, 0))
            ttk.Entry(controls, textvariable=variable).pack(fill="x")
        ttk.Button(controls, text="Add", command=self.add_point).pack(fill="x", pady=(12, 2))
        ttk.Button(controls, text="Modify", command=self.modify_point).pack(fill="x", pady=2)
        ttk.Button(controls, text="Delete", command=self.delete_point).pack(fill="x", pady=2)
        ttk.Button(controls, text="Clear all points", command=self.clear_points).pack(fill="x", pady=(8, 2))
        ttk.Button(controls, text="Add in database", command=self.add_in_database).pack(fill="x", pady=(8, 2))
        ttk.Button(controls, text="Update in database", command=self.update_in_database).pack(fill="x", pady=2)
        ttk.Button(controls, text="Load from database", command=self.load_from_database).pack(fill="x", pady=2)
        ttk.Label(controls, text="Cost criterion").pack(anchor="w", pady=(12, 0))
        ttk.Combobox(controls, textvariable=self.criterion_var, values=("distance", "duration", "monetary_cost", "weighted"), state="readonly").pack(fill="x")
        ttk.Label(controls, text="Distance weight").pack(anchor="w", pady=(6, 0))
        ttk.Entry(controls, textvariable=self.distance_weight_var).pack(fill="x")
        ttk.Label(controls, text="Duration weight").pack(anchor="w", pady=(6, 0))
        ttk.Entry(controls, textvariable=self.duration_weight_var).pack(fill="x")
        ttk.Button(controls, text="Optimize", command=self.optimize).pack(fill="x", pady=(16, 2))
        ttk.Label(controls, textvariable=self.status_var, wraplength=220).pack(anchor="w", pady=12)
        map_frame = ttk.Frame(self.root)
        map_frame.pack(side="right", fill="both", expand=True)
        self.map_view = MapView(map_frame)
        self.map_view.set_click_callback(self._on_map_click)

    def _on_map_click(self, coordinates):
        latitude, longitude = coordinates
        self.latitude_var.set(f"{latitude:.6f}")
        self.longitude_var.set(f"{longitude:.6f}")
        self.status_var.set("Map coordinates selected; edit them if needed")

    def _read_location(self):
        return Location(self.label_var.get().strip().lower().replace(" ", "-"), self.label_var.get(), float(self.latitude_var.get()), float(self.longitude_var.get()))

    def add_point(self):
        try:
            location = self._read_location()
            self.locations.append(location)
            self.current_journey = None
            self.current_result = None
            self.map_view.clear_route()
            self._refresh_points()
        except (ValueError, Exception) as error:
            messagebox.showerror("Invalid point", str(error))

    def modify_point(self):
        selection = self.points.curselection()
        if not selection:
            return
        try:
            replacement = self._read_location()
            old = self.locations[selection[0]]
            self.locations[selection[0]] = replacement
            self.current_journey = None
            self.current_result = None
            self.map_view.clear_route()
            self._refresh_points()
        except (ValueError, Exception) as error:
            messagebox.showerror("Invalid point", str(error))

    def common_delete_point_and_clear_point(self, index=None):
        if index is not None:
            location = self.locations.pop(index)
            self.status_var.set(f"Deleted {location.label}")
        self.current_journey = None
        self.current_result = None
        self.map_view.clear_route()
        self._refresh_points()
        self.label_var.set("")
        self.latitude_var.set("")
        self.longitude_var.set("")
        self.journey_id.set("")

    def delete_point(self):
        selection = self.points.curselection()
        if not selection:
            self.status_var.set("Select a journey point to delete")
            return

        index = selection[0]
        location = self.locations[index]
        self.common_delete_point_and_clear_point(index)

    def clear_points(self):
        self.locations.clear()
        self.common_delete_point_and_clear_point()
        self.status_var.set("All journey points cleared")

    def common_add_and_update_in_database(self, journey):
        try:           
            for location in self.locations:
                self.persistence.save_location(location)
            self.persistence.save_journey(journey)
            if self.current_result is not None:
                self.persistence.save_result(dataclasses.replace(self.current_result, journey_id=journey.id))
                self.journey_id.set(journey.id)
            
        except Exception as error:
            self.status_var.set(f"Database save failed: {error}")

    def add_in_database(self):
        try:
            if not self.locations:
                self.status_var.set("Add at least one journey point first")
                return
            base_journey = self.current_journey or self._build_journey()
            journey = dataclasses.replace(base_journey, id=f"journey-{uuid.uuid4().hex}")
            
            self.common_add_and_update_in_database(journey)
                
            self.current_journey = journey
            self.status_var.set(
                "Journey points and optimization saved in database"
                if self.current_result is not None
                else "Journey points saved in database"
            )
        except Exception as error:
            self.status_var.set(f"Database save failed: {error}")

    def update_in_database(self):
        try:
            if not self.current_journey:
                self.status_var.set("No journey to update")
                return            
            if not self.locations:
                self.status_var.set("Add at least one journey point first")
                return
            
            self.common_add_and_update_in_database(self.current_journey)

            self.status_var.set("Journey and optimization updated in database")
        except Exception as error:
            self.status_var.set(f"Database update failed: {error}")

    def load_from_database(self):
        try:
            journeys = self.persistence.list_journeys()
        except Exception as error:
            self.status_var.set(f"Database load failed: {error}")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load from database")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="Saved journeys").pack(anchor="w", padx=12, pady=(12, 4))
        records = tk.Listbox(dialog, height=12, width=55)
        records.pack(padx=12, pady=4)
        for journey in journeys:
            records.insert(tk.END, f"{journey.id} ({len(journey.locations)} points, {journey.cost_criterion.kind})")
        ttk.Button(
            dialog,
            text="Load selected",
            command=lambda: self._load_selected_journey(dialog, records, journeys),
        ).pack(fill="x", padx=12, pady=(4, 12))
        if not journeys:
            self.status_var.set("No saved journeys in database")

    def _load_selected_journey(self, dialog, records, journeys):
        selection = records.curselection()
        if not selection:
            self.status_var.set("Select a saved journey to load")
            return
        journey = journeys[selection[0]]
        try:
            self.current_journey = journey
            self.journey_id.set(journey.id)  # <-- line added 04/09/2026
            self.locations = list(journey.locations)
            self.current_result = self.persistence.get_result(f"{journey.id}-result")
            self.criterion_var.set(journey.cost_criterion.kind)
            if journey.cost_criterion.weights:
                self.distance_weight_var.set(str(journey.cost_criterion.weights.get("distance", 0)))
                self.duration_weight_var.set(str(journey.cost_criterion.weights.get("duration", 0)))
            self._refresh_points()
            self._show_result(self.current_result)
            dialog.destroy()
        except KeyError:
            self.current_result = None
            self._refresh_points()
            self.status_var.set(f"Loaded journey {journey.id}; no optimization saved")
            dialog.destroy()
        except Exception as error:
            self.status_var.set(f"Database load failed: {error}")

    def _refresh_points(self):
        self.points.delete(0, tk.END)
        for location in self.locations:
            self.points.insert(tk.END, f"{location.label} ({location.latitude}, {location.longitude})")

    def _on_point_selected(self, _event=None):
        selection = self.points.curselection()
        if not selection:
            return
        location = self.locations[selection[0]]
        self.label_var.set(location.label)
        self.latitude_var.set(f"{location.latitude:.6f}")
        self.longitude_var.set(f"{location.longitude:.6f}")

    def optimize(self):
        try:
            if len(self.locations) < 2:
                self.status_var.set("Add at least two points")
                return
            journey = self._build_journey()
            self.current_journey = journey
            self.current_result = None
            self.status_var.set("Optimizing...")
            threading.Thread(target=self._run_optimization, args=(journey,), daemon=True).start()
        except Exception as error:
            self.status_var.set(f"Optimization setup failed: {error}")

    def _run_optimization(self, journey):
        try:
            result = self.optimize_service.execute(journey)
            self.root.after(0, lambda: self._finish_optimization(result))
        except Exception as error:
            self.root.after(0, lambda: self.status_var.set(f"Optimization failed: {error}"))

    def _finish_optimization(self, result):
        try:
            self.current_result = result
            self._show_result(result)
        except Exception as error:
            self.status_var.set(f"Unable to display route: {error}")

    def _show_result(self, result):
        ordered = {location.id: location for location in self.locations}
        ordered_locations = [ordered[location_id] for location_id in result.ordered_location_ids]
        self.map_view.show_result(ordered_locations, result.geometry)
        route = " -> ".join(location.label for location in ordered_locations)
        self.status_var.set(
            f"Exact route: {result.total_cost:.2f} ({result.criterion.kind}) | {route}"
        )

    def _selected_criterion(self):
        kind = self.criterion_var.get()
        if kind == "duration":
            return CostCriterion.duration()
        if kind == "monetary_cost":
            return CostCriterion.monetary_cost()
        if kind == "weighted":
            return CostCriterion.weighted({"distance": float(self.distance_weight_var.get()), "duration": float(self.duration_weight_var.get())})
        return CostCriterion.distance()

    def _build_journey(self):
        origin = self.locations[0]
        destination = self.locations[-1]
        return Journey("active-journey", tuple(self.locations), origin.id, destination.id, self._selected_criterion())
