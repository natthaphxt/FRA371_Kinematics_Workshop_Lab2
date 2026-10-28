import math
import sys
import threading
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import numpy as np
    from roboticstoolbox import Robot
    import swift
    import spatialgeometry as sg
except Exception as e:
    print("[FAIL] import error:", e)
    print("Fix:  pip install -r requirements.txt")
    sys.exit(1)

HERE = Path(__file__).resolve().parent
URDF = HERE / "my_robot" / "robot.urdf"
LAUNCH_TIMEOUT_S = 20

if not URDF.exists():
    print("[FAIL] my_robot/robot.urdf not found - put your LAB1 URDF there")
    sys.exit(1)

# --- 1. the URDF file itself -------------------------------------------------

raw = URDF.read_bytes()
bad_lines = [i for i, line in enumerate(raw.splitlines(), 1) if any(b > 127 for b in line)]
if bad_lines:
    print("[FAIL] robot.urdf has non-ASCII characters (e.g. Thai in a comment) on lines:", bad_lines[:10])
    print("       Windows cannot read the file - delete those characters")
    sys.exit(1)
print("[ok] robot.urdf is plain ASCII")

root = ET.fromstring(raw)

bad_paths = [m.get("filename") for m in root.iter("mesh")
             if not m.get("filename", "").startswith("package://my_robot/meshes/")]
if bad_paths:
    print('[FAIL] every mesh path must look like "package://my_robot/meshes/FILE.stl", these do not:')
    for p in bad_paths:
        print("   ", p)
    sys.exit(1)
print("[ok] mesh paths use package://my_robot/meshes/")

movable = [j for j in root.iter("joint") if j.get("type") != "fixed"]
if len(movable) != 3:
    print(f"[FAIL] Lab 2 needs exactly 3 movable joints, found {len(movable)}:")
    for j in movable:
        print(f"    {j.get('name')} ({j.get('type')})")
    print('       the joint to the end-effector must be type="fixed"')
    sys.exit(1)
print("[ok] 3 movable joints:", ", ".join(f"{j.get('name')} ({j.get('type')})" for j in movable))

bad_axes = []
for j in movable:
    ax = j.find("axis")
    xyz = [float(v) for v in (ax.get("xyz") if ax is not None else "1 0 0").split()]
    if any(v not in (-1.0, 0.0, 1.0) for v in xyz):
        bad_axes.append((j.get("name"), xyz))
if bad_axes:
    print("[FAIL] joint axes must point straight along x, y or z (only 0 and +-1):")
    for name, xyz in bad_axes:
        fix = " ".join(f"{round(v):g}" for v in xyz)
        if all(abs(v - round(v)) < 1e-2 for v in xyz):
            print(f'    {name}: xyz="{" ".join(f"{v:g}" for v in xyz)}"  ->  change to xyz="{fix}"')
        else:
            print(f'    {name}: xyz="{" ".join(f"{v:g}" for v in xyz)}"  ->  tilted axis, fix the joint axis in CAD and re-export')
    sys.exit(1)
print("[ok] joint axes are straight")

# --- 2. load it the same way Lab2_PartB.ipynb does ---------------------------

if hasattr(Robot, "URDF_read"):             # older roboticstoolbox
    links, name = Robot.URDF_read("my_robot/robot.urdf", tld=HERE.as_posix())[:2]
else:                                       # roboticstoolbox 1.5 and newer
    from roboticstoolbox.models.URDF import URDFRobot
    from xacrodoc.packages import update_package_cache
    update_package_cache({"my_robot": HERE.as_posix() + "/my_robot"})
    links, name = URDFRobot.URDF_read(HERE.as_posix() + "/my_robot/robot.urdf")[:2]
robot = Robot(links, name=name)
print(f"[ok] loaded '{name}'  ({robot.n} joints)")

missing = [g.filename for link in robot.links for g in link.geometry
           if getattr(g, "filename", None) and not Path(g.filename).exists()]
if missing:
    print("[FAIL] these mesh files were not found - fix the paths or add the files:")
    for m in missing:
        print("   ", m)
    sys.exit(1)
print("[ok] all mesh files found")

# --- 3. can the tip reach a 3-D target? --------------------------------------

lo, hi = robot.qlim
rng = np.random.default_rng(0)
rank = max(np.linalg.matrix_rank(robot.jacob0(lo + (hi - lo) * rng.uniform(0.2, 0.8, robot.n))[:3], tol=1e-6)
           for _ in range(5))
if rank < 3:
    print(f"[FAIL] the tip can only move in {rank} directions, Lab 2 needs x, y and z")
    print("       usually the end-effector sits on the last joint axis - add a fixed joint out to the real tip")
    sys.exit(1)
print("[ok] the tip moves in x, y and z")

if robot.ee_links[0].isjoint:
    print(f"[warn] no fixed end-effector link: the tip is the origin of '{robot.ee_links[0].name}'")
    print("       make sure that is where your gripper tip really is")

print("[ok] tip at q = 0 :", np.round(robot.fkine(np.zeros(robot.n)).t, 4), "m  (compare with your MDH model)")
print("[ok] ready for Lab 2")

# --- 4. look at it in Swift --------------------------------------------------


def build_sliders(robot):
    q = np.zeros(robot.n)
    sliders = []

    def make_cb(idx, is_revolute):
        def cb(value):
            v = float(value)
            q[idx] = math.radians(v) if is_revolute else v
            robot.q = q
        return cb

    idx = 0
    for link in robot.links:
        if not link.isjoint:
            continue
        is_rev = link.v.axis.startswith("R")
        lo, hi = link.qlim if link.qlim is not None else (-math.pi, math.pi)
        if is_rev:
            lo, hi = math.degrees(lo), math.degrees(hi)
        lo, hi = round(lo, 2), round(hi, 2)

        unit = "deg" if is_rev else "m"
        rp = "R" if is_rev else "P"
        desc = f"{link.name} ({rp}) [{lo:.2f}..{hi:.2f} {unit}]"

        slider = swift.Slider(make_cb(idx, is_rev), min=lo, max=hi, step=0.01, value=0.0, desc=desc, unit=unit)
        sliders.append(slider)
        idx += 1

    return q, sliders


env = swift.Swift()
launch_error = {}


def do_launch():
    try:
        env.launch(realtime=True)
    except Exception as e:
        launch_error["e"] = e


t = threading.Thread(target=do_launch, daemon=True)
t.start()
t.join(timeout=LAUNCH_TIMEOUT_S)

if t.is_alive():
    print(f"[FAIL] Swift did not connect to a browser within {LAUNCH_TIMEOUT_S}s")
    sys.exit(1)
if "e" in launch_error:
    print(f"[FAIL] Swift failed to launch: {launch_error['e']}")
    sys.exit(1)

env.add(robot, robot_alpha=0.75)

frame_axes = [sg.Axes(length=0.15) for _ in robot.fkine_all(np.zeros(robot.n))]
for ax in frame_axes:
    env.add(ax)

q, sliders = build_sliders(robot)
for slider in sliders:
    env.add(slider)


def reset_cb(_):
    q[:] = 0.0
    robot.q = q
    for slider in sliders:
        slider.value = 0.0


env.add(swift.Button(reset_cb, desc="Reset to home (q=0)"))

print("[ok] your robot is shown in the browser with joint sliders - press Ctrl+C here to close")

try:
    while True:
        T_all = robot.fkine_all(q)
        for ax, T in zip(frame_axes, T_all):
            ax.T = T.A
        env.step(0.05)
except KeyboardInterrupt:
    pass
finally:
    try:
        env.close()
    except Exception:
        pass
    print("closed.")
