import sys
import argparse
import debugpy
from accelerate.commands.accelerate_cli import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debugging.")
    parser.add_argument(
        "--debug-port", type=int, default=5678, help="Debug port (default: 5678)"
    )

    args, remaining_args = parser.parse_known_args()

    if args.debug:
        debugpy.listen(args.debug_port)
        print(f"Waiting for debugger attach on port {args.debug_port}...")
        debugpy.wait_for_client()
        print("Debugger attached!")

    sys.argv = [sys.argv[0]] + remaining_args

    if sys.argv[0].endswith('.exe'):
        sys.argv[0] = sys.argv[0][:-4]
    sys.exit(main())