
import os

file_path = r"c:\Users\arman\Documents\repos\kubesight\src\views\controllers_view.py"

with open(file_path, "r") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Remove lines 512 to 706 (indices 511 to 706 in slice notation for [start:end] where end is exclusive? No, list slicing is [start:end_exclusive])
# Line 512 is index 511.
# Line 706 is index 705.
# We want to remove indices 511 to 705 inclusive.
# So we keep :511 and 706:

new_lines = lines[:511] + lines[706:]

print(f"New line count: {len(new_lines)}")

with open(file_path, "w") as f:
    f.writelines(new_lines)

print("File updated.")
