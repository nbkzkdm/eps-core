from eps.store import load_store, save_store


def register(subparsers):
    parser = subparsers.add_parser(
        "entry",
        help="Register a command",
        description="Register a reusable command. Use $1, $2 ... as placeholders for runtime input."
    )

    parser.add_argument("command", nargs="+")
    parser.add_argument("-n", "--name", help="Entry name (optional)")
    parser.add_argument("--force", action="store_true")
    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()

    command_str = " ".join(args.command)

    name = args.name if args.name else command_str.replace(" ", "-").lower()

    entries = store.setdefault("entries", [])

    for entry in entries:
        if entry["name"] == name:
            if not args.force:
                print(f"[ERROR] Entry '{name}' already exists.")
                print("Use --force to overwrite.")
                return

            entry["command"] = command_str
            save_store(store)
            print(f"[OK] updated: {name} -> {command_str}")
            return

    entries.append({
        "name": name,
        "command": command_str
    })

    save_store(store)
    print(f"[OK] registered: {name} -> {command_str}")
