from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def asset_path(relative_path):
    # Resolve assets from the project folder, not from the terminal's cwd.
    return str(PROJECT_ROOT / relative_path)
