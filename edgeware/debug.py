import subprocess
import sys

from src.paths import Process

# TODO: Running individual features
print("""Which feature would you like to run?
0. Quit
1. Edgeware (start.py)
2. Config (config.py)""")

processes = [
    [Process.MAIN],
    [Process.CONFIG]
]  # fmt: off

while True:
    num = input("Select number: ")
    try:
        num = int(num)
    except Exception:
        print("Input must be an integer")
        continue

    if num == 0:
        break
    elif num > 0 and num <= len(processes):
        subprocess.run([sys.executable] + processes[num - 1])
        print("Done")
    else:
        print("Input must be between 0 and 2")

print("Goodbye!")
