import sys
import argparse
import subprocess
from pathlib import Path
import os
from neuronpyxl import ModBuilder

parser = argparse.ArgumentParser(
        description="Execute a Python script from a given file path."
)

parser.add_argument(
    "--name",
    required=True,
    type=str,
    help="Name of the script to run.",
)

parser.add_argument(
    "--snnap_data",
    type=Path,
    default=Path(f"{os.environ["HOME"]}/Downloads"),
    help="Path to SNNAP data.",
)

def check_path(path:Path):
    if not path.exists():
        print(f"Error: File '{path}' does not exist.")
        sys.exit(1)

def check_file(path:Path):
    if not path.is_file():
        print(f"Error: '{path}' is not a file.")
        sys.exit(1)


def main():
    Path("./data").mkdir(parents=True, exist_ok=True)
    Path("./figs").mkdir(parents=True, exist_ok=True)

    args = parser.parse_args()
    script_name = args.name

    script_path = Path(f"./scripts/{script_name}.py")
    snnap_path = args.snnap_data
    
    check_path(script_path)
    check_file(script_path)
    check_path(snnap_path)

    try:
        subprocess.run([
                        sys.executable,
                        str(script_path),
                        "--snnap_data",
                        str(snnap_path),
                        ],
                        check=True
                    )
    except subprocess.CalledProcessError as e:
        print(f"Script exited with non-zero status: {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()