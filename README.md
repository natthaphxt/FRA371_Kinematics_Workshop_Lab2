# FRA371_Kinematics_Workshop_Lab2

![Course](https://img.shields.io/badge/Course-FRA371-blue)
![Workshop](https://img.shields.io/badge/Workshop-Lab2-green)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?logo=python&logoColor=white)

## Swift Setup

Set up Swift exactly the way Lab 2 uses it, and confirm it shows a robot inside the notebook.

### 1. Install

```
pip install -r requirements.txt
python fix_swift.py
```

- `requirements.txt` pins `websockets==12.0` so Swift does not hang
- `fix_swift.py` fixes robot meshes not showing in Swift on **Windows** (safe to run on macOS/Linux)

### When to run `fix_swift.py`

`fix_swift.py` patches the Swift package installed in your Python, not this project, so:

- **Run it once, right after `pip install`**, before you open the notebook.
- **Run it with the same Python as your notebook kernel.** If you use a venv, activate it first.
- **Run it again after every reinstall of Swift**: a new venv, a new computer, or `pip install --upgrade`. Reinstalling puts the unpatched file back.
- **Restart the kernel** if the notebook was already open when you ran it.

Running it twice is fine, it prints `already patched`.

### 2. Open the practice notebook

1. Open `practice.ipynb` in VS Code and pick a **Python 3.10–3.12** kernel.
2. Run the **0 - Setup** cell. The toy arm should appear under the cell — then Swift is ready for Lab 2.
3. Run the rest top to bottom, filling in the lines marked `# edit here`.

## Target

Copy these into section 2 of `practice.ipynb`. All values are in metres.

- **`M`** is the object position reported by the camera, in the **camera frame**.
- **`T`** is the homogeneous transformation matrix of the **base frame w.r.t. the camera frame**.

```
M = [ 0.10, -0.10, 0.85 ]

    [   1.0000    0.0000    0.0000   -0.1000 ]
T = [   0.0000   -1.0000    0.0000    0.0500 ]
    [   0.0000    0.0000   -1.0000    0.9000 ]
    [   0.0000    0.0000    0.0000    1.0000 ]
```

## Files

- **`practice.ipynb`** — RTB practice notebook, inverse kinematics basics, shown in Swift.
- **`toy_robot/`** — toy 2-link arm (URDF + STL meshes), loaded the same way as your robot in Lab 2.
- **`fix_swift.py`**, **`requirements.txt`** — same install as Lab 2.

## Troubleshooting

| Problem | Fix |
|---|---|
| Swift **hangs** at `env.launch` | `pip install "websockets==12.0"`, then restart the kernel |
| Arm **does not show** / *"a client-side exception has occurred"* (Windows) | `python fix_swift.py`, then restart the kernel |
| `fix_swift.py` prints `target line not found` | see **Manual fix** below |
| `FileNotFoundError: toy_robot/robot.urdf` | open this project folder as the VS Code workspace |

### Manual fix

Open `SwiftRoute.py` in the folder printed by `python -c "import swift, os; print(os.path.dirname(swift.__file__))"`.
Find the line with `urllib.parse.unquote(self.path[9:])` and add these two lines right after it, at the same indent:

```python
if os.name == "nt" and len(self.path) > 2 and self.path[0] == "/" and self.path[2] == ":":
    self.path = self.path[1:]  # Windows drive path fix
```
