# src/SatisPlanning/utils.py
import os

def asset_path(relative_path: str) -> str:
    """Devuelve la ruta absoluta del asset desde el archivo actual."""
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "assets", relative_path)

