import subprocess
import sys

from watchfiles import run_process


def start():
    subprocess.run([sys.executable, "src/bot.py"], check=True)


if __name__ == "__main__":
    run_process("src/", target=start)
