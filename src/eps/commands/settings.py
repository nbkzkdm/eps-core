from eps.store import load_store, save_store


def register(subparsers):
    parser = subparsers.add_parser(
        "settings",
        help="View or modify EPS settings",
        description="View or modify EPS settings."
    )

    settings_subparsers = parser.add_subparsers(
        dest="settings_command",
        required=True
    )

    view_parser = settings_subparsers.add_parser(
        "view",
        help="View settings"
    )
    view_parser.set_defaults(handler=handle_view)

    modify_parser = settings_subparsers.add_parser(
        "modify",
        help="Modify a setting"
    )
    modify_parser.add_argument("key")
    modify_parser.set_defaults(handler=handle_modify)


def handle_view(args):
    store = load_store()
    settings = store["settings"]

    print(f"save.file.path: {settings['save']['file']['path']}")
    print(f"save.file.name: {settings['save']['file']['name']}")


def handle_modify(args):
    store = load_store()
    settings = store["settings"]

    key_map = {
        "save.file.path": ("save", "file", "path"),
        "save.file.name": ("save", "file", "name"),
    }

    if args.key not in key_map:
        print(f"[ERROR] Unknown setting: {args.key}")
        return

    keys = key_map[args.key]
    current = settings[keys[0]][keys[1]][keys[2]]

    print(f"[CURRENT] {args.key}: {current}")
    new_value = input("[NEW VALUE] ").strip()

    if not new_value:
        print("[CANCEL] setting was not changed.")
        return

    settings[keys[0]][keys[1]][keys[2]] = new_value
    save_store(store)

    print(f"[OK] updated: {args.key} -> {new_value}")
