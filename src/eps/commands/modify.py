from eps.store import load_store, save_store


def register(subparsers):
    parser = subparsers.add_parser(
        "modify",
        help="Modify a registered command",
        description="Modify the command text of a registered entry."
    )

    parser.add_argument("name", help="Entry name")
    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()
    entries = store.get("entries", [])

    entry = next((e for e in entries if e["name"] == args.name), None)

    if not entry:
        print(f"[ERROR] Entry '{args.name}' does not exist.")
        return

    print(f"[ENTRY] {entry['name']}")
    print(f"[CURRENT] {entry['command']}")

    new_command = input("[NEW COMMAND] ").strip()

    if not new_command:
        print("[CANCEL] command was not changed.")
        return

    entry["command"] = new_command
    save_store(store)

    print(f"[OK] modified: {entry['name']} -> {new_command}")

