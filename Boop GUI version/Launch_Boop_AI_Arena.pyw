from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "boop" / "main.py"


def main():
    subprocess.Popen([sys.executable, str(SCRIPT)], cwd=str(ROOT))


if __name__ == "__main__":
    main()
