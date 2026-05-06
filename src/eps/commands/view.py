from eps.store import load_store


def register(subparsers):
    parser = subparsers.add_parser(
        "view",
        help="View registered commands",
        description="Display a registered command or list all commands."
    )

    parser.add_argument("name", nargs="?")
    parser.add_argument("-a", "--all", action="store_true")

    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()
    entries = store.get("entries", [])

    if args.all:
        for e in entries:
            print(f"[ENTRY] {e['name']}")
            print(f"[COMMAND] {e['command']}")
            print()
        return

    if not args.name:
        print("[ERROR] name required or use --all")
        return

    entry = next((e for e in entries if e["name"] == args.name), None)

    if not entry:
        print(f"[ERROR] Entry '{args.name}' does not exist.")
        return

    print(f"[ENTRY] {entry['name']}")
    print(f"[COMMAND] {entry['command']}")

