import json
from pathlib import Path

from eps.store import load_store, save_store


def register(subparsers):
    parser = subparsers.add_parser(
        "load",
        help="Load entries from a JSON file",
        description="Load entries and merge into current store."
    )

    parser.add_argument("file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--skip", action="store_true", help="Skip duplicated entries")
    group.add_argument("-f", "--force", action="store_true", help="Overwrite duplicated entries")
    parser.set_defaults(handler=handle)


def handle(args):
    file_path = Path(args.file).expanduser()

    if not file_path.exists():
        print(f"[ERROR] File does not exist: {file_path}")
        return

    try:
        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON format: {e}")
        return

    if not isinstance(loaded_data, dict) or "entries" not in loaded_data:
        print("[ERROR] Invalid format: 'entries' is required.")
        return

    loaded_entries = loaded_data["entries"]

    if not isinstance(loaded_entries, list):
        print("[ERROR] Invalid format: 'entries' must be a list.")
        return

    # validation
    for i, e in enumerate(loaded_entries):
        if not isinstance(e, dict) or "name" not in e or "command" not in e:
            print(f"[ERROR] Invalid format at entries[{i}]")
            return

    store = load_store()
    current_entries = store.setdefault("entries", [])

    name_map = {e["name"]: e for e in current_entries}

    added = 0
    skipped = 0
    overwritten = 0

    for entry in loaded_entries:
        name = entry["name"]
        command = entry["command"]

        if name in name_map:
            if args.skip:
                skipped += 1
                print(f"[SKIP] {name}")
                continue

            if args.force:
                name_map[name]["command"] = command
                overwritten += 1
                print(f"[OVERWRITE] {name}")
                continue

            # rename
            new_name = resolve_name(name, name_map)
            current_entries.append({
                "name": new_name,
                "command": command
            })
            name_map[new_name] = current_entries[-1]

            added += 1
            print(f"[RENAME] {name} -> {new_name}")
            continue

        # new entry
        current_entries.append({
            "name": name,
            "command": command
        })
        name_map[name] = current_entries[-1]
        added += 1

    save_store(store)

    print(f"[OK] load complete")
    print(f"  added: {added}")
    print(f"  overwritten: {overwritten}")
    print(f"  skipped: {skipped}")


def resolve_name(name, name_map):
    counter = 2

    while True:
        candidate = f"{name}{counter}"
        if candidate not in name_map:
            return candidate
        counter += 1
