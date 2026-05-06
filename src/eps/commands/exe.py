import re
import subprocess
from eps.store import load_store

ARG_PATTERN = re.compile(r"\$(\d+)")


def register(subparsers):
    parser = subparsers.add_parser(
        "exe",
        help="Execute a registered command",
        description="Execute a registered command. Runtime arguments can be passed directly or entered interactively."
    )
    parser.add_argument("name", help="Entry name")
    parser.add_argument(
        "values",
        nargs="*",
        help="Values for $1, $2, ... placeholders"
    )

    parser.set_defaults(handler=handle)


def handle(args):
    store = load_store()
    entries = store.get("entries", [])

    entry = next((e for e in entries if e["name"] == args.name), None)

    if not entry:
        print(f"[ERROR] Entry '{args.name}' does not exist.")
        return

    command = entry["command"]

    arg_numbers = sorted({
        int(m.group(1))
        for m in ARG_PATTERN.finditer(command)
    })

    required_count = len(arg_numbers)
    given_count = len(args.values)

    if given_count > required_count:
        print("[ERROR] Too many arguments.")
        print(f"Required: {required_count}")
        print(f"Given: {given_count}")
        return

    values = {}

    for index, number in enumerate(arg_numbers):
        if index < given_count:
            values[number] = args.values[index]
        else:
            values[number] = input(f"args{number}: ")

    executed = command

    for number, value in values.items():
        executed = executed.replace(f"${number}", value)

    print(f"[COMMAND] {executed}")
    print("[RESULT]")

    result = subprocess.run(
        executed,
        shell=True,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="")

    if result.returncode != 0:
        print(f"[ERROR] exit code {result.returncode}")
