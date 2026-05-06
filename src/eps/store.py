import json
from pathlib import Path


DEFAULT_STORE = {
    "entries": [],
    "settings": {
        "save": {
            "file": {
                "path": "~",
                "name": "eps-settings.json"
            }
        }
    }
}


def get_store_path():
    return Path.home() / ".eps" / "store.json"


def load_store():
    store_path = get_store_path()

    if not store_path.exists():
        store_path.parent.mkdir(parents=True, exist_ok=True)
        save_store(DEFAULT_STORE)

    data = json.loads(store_path.read_text(encoding="utf-8"))

    data.setdefault("entries", [])
    data.setdefault("settings", {})
    data["settings"].setdefault("save", {})
    data["settings"]["save"].setdefault("file", {})
    data["settings"]["save"]["file"].setdefault("path", "~")
    data["settings"]["save"]["file"].setdefault("name", "eps-settings.json")

    return data


def save_store(data):
    store_path = get_store_path()
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )