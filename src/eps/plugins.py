from importlib.metadata import entry_points

ENTRY_POINT_GROUP = "eps.commands"


def load_command_plugins(subparsers):
    eps = entry_points()

    if hasattr(eps, "select"):
        commands = eps.select(group=ENTRY_POINT_GROUP)
    else:
        commands = eps.get(ENTRY_POINT_GROUP, [])

    loaded = set()

    for ep in commands:
        if ep.name in loaded:
            continue

        loaded.add(ep.name)

        register = ep.load()
        register(subparsers)

