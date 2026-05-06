from eps.store import load_store, save_store


def register(subparsers):
    parser = subparsers.add_parser(
        "delete",
        help="Delete registered command entry",
        description="Delete an entry by name or delete all entries with confirmation."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "name",
        nargs="?",
        help="Entry name"
    )
    group.add_argument(
        "-a", "--all",
        action="store_true",
        help="Delete all entries"
    )

    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()
    entries = store.get("entries", [])

    # --- 全削除 ---
    if args.all:
        if not entries:
            print("[INFO] No entries to delete.")
            return

        print("[WARNING] This will delete ALL entries.")
        print(f"[COUNT] {len(entries)} entries")

        confirm = input("Delete ALL entries? [y/N]: ").strip().lower()

        if confirm not in ("y", "yes"):
            print("[CANCEL] delete canceled.")
            return

        store["entries"] = []
        save_store(store)

        print("[OK] all entries deleted.")
        return

    # --- 単体削除 ---
    entry = next((e for e in entries if e["name"] == args.name), None)

    if entry is None:
        print(f"[ERROR] Entry '{args.name}' does not exist.")
        return

    print(f"[ENTRY] {entry['name']}")
    print(f"[COMMAND] {entry['command']}")

    confirm = input("Delete this entry? [y/N]: ").strip().lower()

    if confirm not in ("y", "yes"):
        print("[CANCEL] delete canceled.")
        return

    store["entries"] = [e for e in entries if e["name"] != args.name]
    save_store(store)

    print(f"[OK] deleted: {args.name}")

