import argparse
from eps.plugins import load_command_plugins


def build_parser():
    parser = argparse.ArgumentParser(
        prog="eps",
        description="EPS (Entry Point System): Register and execute reusable shell commands with arguments.",
        epilog="""
Examples:
  eps entry echo '$1' --name sample01
  eps exe sample01
  eps view sample01
  eps view --all
  eps modify sample01
  eps delete sample01
""", formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar=""
    )

    load_command_plugins(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
