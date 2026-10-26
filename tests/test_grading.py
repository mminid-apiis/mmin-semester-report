"""Uji aturan status. Jalankan: python tests/test_grading.py (pakai Python dari .venv)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.grading import STATUS_FAIL, STATUS_PASS, STATUS_WARN, classify  # noqa: E402

CASES = [
    # (kuis, kehadiran, status, catatan)
    (88, 95, STATUS_PASS, "jelas lulus"),
    (70, 75, STATUS_PASS, "tepat di batas hijau"),
    (69.9, 95, STATUS_WARN, "kuis sedikit di bawah 70"),
    (95, 74.9, STATUS_WARN, "kehadiran sedikit di bawah 75"),
    (95, 72, STATUS_WARN, "kehadiran 70-75 = kuning, bukan merah"),
    (82, 68, STATUS_WARN, "kehadiran 68"),
    (65, 90, STATUS_WARN, "kuis 65"),
    (50, 50, STATUS_WARN, "tepat 50 masih kuning"),
    (50, 95, STATUS_WARN, "kuis tepat 50"),
    (49.9, 95, STATUS_FAIL, "kuis di bawah 50"),
    (95, 49.9, STATUS_FAIL, "kehadiran di bawah 50"),
    (10, 10, STATUS_FAIL, "keduanya rendah"),
    (0, 0, STATUS_FAIL, "nol"),
    (100, 100, STATUS_PASS, "penuh"),
    (None, 90, None, "kuis kosong"),
    (90, None, None, "kehadiran kosong"),
    (None, None, None, "keduanya kosong"),
]

failed = 0
for kuis, hadir, expected, note in CASES:
    got = classify(kuis, hadir)
    if got != expected:
        failed += 1
        print(f"FAIL kuis={kuis} hadir={hadir}: expected {expected}, got {got} ({note})")

print(f"{len(CASES) - failed} passed, {failed} failed")
sys.exit(1 if failed else 0)
