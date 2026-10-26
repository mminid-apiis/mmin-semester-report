"""Aturan status siswa (hijau / kuning / merah) -- satu-satunya tempat angka ini ditulis.

Angka-angka ini TIDAK PERNAH ditampilkan ke siswa (lihat lib/report_view.py);
siswa hanya melihat salah satu dari tiga pesan status.

  hijau  ("pass"): kuis >= KUIS_MIN dan kehadiran >= KEHADIRAN_MIN
  merah  ("fail"): kuis ATAU kehadiran < AMBANG_BAWAH
  kuning ("warn"): selain itu -- lulus semester 2 dengan syarat
"""

from __future__ import annotations

KUIS_MIN = 70
KEHADIRAN_MIN = 75
AMBANG_BAWAH = 50

STATUS_PASS = "pass"
STATUS_WARN = "warn"
STATUS_FAIL = "fail"


def classify(kuis: float | None, kehadiran: float | None) -> str | None:
    """None kalau salah satu nilai belum ada (status tidak bisa ditentukan)."""
    if kuis is None or kehadiran is None:
        return None
    if kuis < AMBANG_BAWAH or kehadiran < AMBANG_BAWAH:
        return STATUS_FAIL
    if kuis >= KUIS_MIN and kehadiran >= KEHADIRAN_MIN:
        return STATUS_PASS
    return STATUS_WARN
