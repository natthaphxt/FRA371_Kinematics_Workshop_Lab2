# FRA371_Kinematics_Workshop_Lab2

![Course](https://img.shields.io/badge/Course-FRA371-blue)
![Workshop](https://img.shields.io/badge/Workshop-Lab2-green)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?logo=python&logoColor=white)

ซ้อมก่อนทำ **Lab 2 : Inverse Kinematics**

1. ฝึก flow ทั้งหมดของ Lab 2 กับหุ่น toy ที่รู้คำตอบแน่นอน (`practice.ipynb`)
2. เช็คว่าหุ่นของกลุ่มจาก LAB1 พร้อมใช้ใน Lab 2 (`check_robot.py`)

---

## 1. Install

```
pip install -r requirements.txt
python fix_swift.py
```

- `fix_swift.py` = แก้ให้เมชแสดงใน Swift บน **Windows** (บน macOS/Linux รันได้ ไม่มีผลเสีย)
- `requirements.txt` ล็อก `websockets==12.0` ไว้กัน Swift ค้าง

## 2. Practice : toy robot

1. เปิด `practice.ipynb` ใน VS Code แล้วเลือก kernel เป็น **Python 3.10–3.12**
2. รันทีละเซลล์จากบนลงล่าง เติมเฉพาะบรรทัดที่มี `# edit here`

> อย่ากด Run All เพราะเซลล์ถัดไปต้องใช้คำตอบจากเซลล์ก่อนหน้า

| Section | ทำอะไร | ตรงกับ Lab 2 |
|---|---|---|
| 0.1 – 0.2 | โหลดหุ่น toy ขึ้น Swift แล้ว cross-check MDH vs URDF | Part B Setup |
| A1 | แปลงตำแหน่งชิ้นงานจาก camera frame เป็น base frame ด้วย inverse ของ `T` | Part A ข้อ 1 |
| A2 | เขียนสมการ IK ของหุ่น toy ให้ครบทั้ง 4 branch | Part A ข้อ 2–4 |
| B1 | วางลูกบอลแดงที่เป้าหมาย แล้วส่งหุ่นไปที่ `q_goal` | Part B ข้อ 1 |
| B2 | cross-check ด้วย FK: ระยะจาก `tip` ถึง `M` | Part B ข้อ 2 |
| B3 | ให้ `ikine_LM` หา IK แล้วเทียบกับ branch ที่คิดเอง | Part B ข้อ 3 |
| B4 | เช็คทุก branch ด้วย FK และดูหุ่นเปลี่ยนท่าใน Swift | Part B ข้อ 4 |

ผ่านเมื่อ: `MDH vs URDF: OK`, `diff` ใน A1 ใกล้ 0 และทุก branch ได้ `err` ≤ **0.03 m**

## 3. Check your robot

หุ่นมาจาก URDF exporter ของ CAD: ไฟล์ `.urdf` 1 ไฟล์ + เมช `.stl` หลายไฟล์

1. วางไฟล์เมชไว้ใน `my_robot/meshes/`
2. บันทึก URDF เป็น `my_robot/robot.urdf`
3. ทุก path เมชใน `robot.urdf` ต้องเป็น

```xml
<mesh filename="package://my_robot/meshes/YOUR_FILE.stl"/>
```

แล้วรัน (ไม่ต้องใส่ argument)

```
python check_robot.py
```

ต้องได้ `[ok] ready for Lab 2` แล้วหุ่นจะเปิดใน Swift พร้อม slider ของแต่ละ joint ถ้าเจอ `[FAIL]` ให้แก้ตามข้อความแล้วรันใหม่

ตัวเช็คดูว่า

- `robot.urdf` เป็น ASCII ล้วน (คอมเมนต์ภาษาไทยทำให้ Windows อ่านไฟล์ไม่ได้)
- path เมชทุกอันเป็น `package://my_robot/meshes/...` และเจอไฟล์ครบ
- มี joint ที่ขยับได้ **3 ตัวพอดี** (joint ที่ต่อไปยัง end-effector ต้องเป็น `type="fixed"`)
- แกน joint ตรง เช่น `xyz="0 0 1"` (มีแค่ 0 กับ ±1)
- ปลายมือขยับได้ครบทั้ง x, y, z (end-effector ไม่ได้อยู่บนแกน joint สุดท้าย)
- พิมพ์ตำแหน่ง tip ที่ `q = 0` ไว้เทียบกับตาราง MDH ของ LAB1

## Files

- **`practice.ipynb`** — IK warm-up กับหุ่น toy ตามลำดับเดียวกับ Lab 2
- **`check_robot.py`** — `python check_robot.py` เช็คหุ่นใน `my_robot/` ว่าพร้อมสำหรับ Lab 2 แล้วเปิดใน Swift
- **`toy_robot/robot.urdf`** — หุ่น toy 3-DOF (RRR) ทำจากรูปทรงพื้นฐาน ไม่มีไฟล์เมช
- **`my_robot/`** — ใส่หุ่นของกลุ่มจาก LAB1 ที่นี่
- **`fix_swift.py`**, **`requirements.txt`** — ชุดติดตั้งเดียวกับ Lab 2

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Swift **ค้าง** ตอน `env.launch` | `pip install "websockets==12.0"` |
| หุ่น **ไม่ขึ้น** / *"a client-side exception has occurred"* (Windows) | รัน `python fix_swift.py` แล้ว **Restart kernel** |
| `fix_swift.py` บอก `target line not found` | ดู **Manual fix** ด้านล่าง |
| `FileNotFoundError: toy_robot/robot.urdf` | เปิดโฟลเดอร์โปรเจกต์นี้เป็น workspace ของ VS Code |
| `UnicodeDecodeError` ตอนโหลด URDF | ไฟล์ URDF ต้องเป็น **ASCII ล้วน** (คอมเมนต์ห้ามมีอักษรไทย) |
| หุ่นขึ้นแต่ **เมชมองไม่เห็น** | ชื่อ `package://` ใน URDF ต้องตรงกับชื่อโฟลเดอร์ (`my_robot`) |
| `ValueError: incorrect vector length` | หุ่นต้องมี joint ที่ขยับได้ 3 ตัวพอดี joint ที่ต่อไปยัง end-effector ต้องเป็น `type="fixed"` |
| `MDH vs URDF: NOT MATCHING` ทั้งที่ตาราง MDH ถูก | เช็ค `<axis xyz="..."/>` ใน URDF ต้องเป็นแกนตรง และท่าศูนย์ของแต่ละ joint ต้องตรงกับ `offset=` ในตาราง MDH |

### Manual fix

เปิดไฟล์ `SwiftRoute.py` ในโฟลเดอร์ที่ได้จาก `python -c "import swift, os; print(os.path.dirname(swift.__file__))"`
หาบรรทัดที่มี `urllib.parse.unquote(self.path[9:])` แล้วเพิ่มสองบรรทัดนี้ต่อท้าย (ย่อหน้าเท่ากับบรรทัดนั้น)

```python
if os.name == "nt" and len(self.path) > 2 and self.path[0] == "/" and self.path[2] == ":":
    self.path = self.path[1:]  # Windows drive path fix
```
