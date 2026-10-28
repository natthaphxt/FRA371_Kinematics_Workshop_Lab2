"""
One-time fix for swift-sim on Windows (run once after installing requirements):

    python fix_swift.py

Bug: SwiftRoute serves mesh files with a leading '/' before the drive letter
(e.g. '/D:/..'), which open() rejects on Windows -> every mesh 404s and the 3D
viewer crashes with "Application error: a client-side exception has occurred".
This inserts a one-line fix so the path opens correctly. Safe to run repeatedly.
(Not needed on macOS/Linux, but harmless.)
"""
import os

try:
    import swift
except ImportError:
    raise SystemExit("swift not installed - run first:  pip install -r requirements.txt")

path = os.path.join(os.path.dirname(swift.__file__), "SwiftRoute.py")
src = open(path, encoding="utf-8").read()

if "Windows drive path fix" in src:
    print("already patched:", path)
else:
    out, done = [], False
    for line in src.splitlines(keepends=True):
        out.append(line)
        if not done and "urllib.parse.unquote(self.path[9:])" in line:
            indent = line[: len(line) - len(line.lstrip())]
            out.append(indent + 'if os.name == "nt" and len(self.path) > 2 '
                                'and self.path[0] == "/" and self.path[2] == ":":\n')
            out.append(indent + "    self.path = self.path[1:]  # Windows drive path fix\n")
            done = True
    if done:
        open(path, "w", encoding="utf-8").write("".join(out))
        print("patched:", path)
    else:
        print("target line not found - your swift version differs; see README 'Manual fix'.")
