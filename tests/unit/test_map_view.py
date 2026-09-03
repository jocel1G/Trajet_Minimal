from src.presentation.map_view import MapView


def test_map_view_fallback_is_available_without_map_dependency(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "tkintermapview", None)
    assert MapView is not None
