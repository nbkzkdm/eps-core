import json
from pathlib import Path

from eps.store import load_store


def register(subparsers):
    parser = subparsers.add_parser(
        "save",
        help="Save entries to settings file",
        description="Save registered entries to the configured settings file."
    )

    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()
    settings = store["settings"]["save"]["file"]

    save_dir = Path(settings["path"]).expanduser()
    save_path = save_dir / settings["name"]

    data = {
        "entries": [
            {
                "name": entry["name"],
                "command": entry["command"]
            }
            for entry in store.get("entries", [])
        ]
    }

    if save_path.exists():
        print(f"[INFO] File already exists: {save_path}")
        answer = input("Overwrite this file? [y/N]: ").strip().lower()

        if answer not in ("y", "yes"):
            print("[CANCEL] save canceled.")
            return

    save_dir.mkdir(parents=True, exist_ok=True)

    save_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"[OK] saved: {save_path}")

