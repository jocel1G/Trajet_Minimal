import tkinter as tk

from src.application.optimize_journey import OptimizeJourney
from src.config import Settings
from src.persistence.sqlite_adapter import SQLitePersistence
from src.presentation.journey_window import JourneyWindow
from src.routing.adapters.deterministic import DeterministicRoutingProvider


def main():
    settings = Settings.from_environment()
    persistence = SQLitePersistence(settings.db_path)
    provider = DeterministicRoutingProvider()
    service = OptimizeJourney(provider, settings.exact_point_limit, settings.provider_timeout_seconds)
    root = tk.Tk()
    JourneyWindow(root, service, persistence)
    root.mainloop()
    persistence.close()


if __name__ == "__main__":
    main()
