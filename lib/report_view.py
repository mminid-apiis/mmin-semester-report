"""Kartu hasil laporan siswa (nama, status keseluruhan, rata-rata kuis & kehadiran).

Sengaja TIDAK menampilkan ambang kelulusan, penanda "passing", maupun status
lulus/tidak per kriteria -- hanya satu status akhir. Gaya CSS-nya ada di
lib/branding.py (kelas `mm-*`).
"""

from __future__ import annotations

import html
import math


def format_percent(value: float | None) -> str:
    """Angka tanpa desimal kalau bulat, selain itu satu desimal (dipotong, bukan
    dibulatkan, supaya angka yang tampil tidak pernah >= batas tapi berstatus belum)."""
    if value is None:
        return "-"
    truncated = math.floor(round(value * 10, 6)) / 10
    return f"{truncated:.0f}" if truncated == int(truncated) else f"{truncated:.1f}"


def _tile(label: str, value: float | None, bar_class: str) -> str:
    shown = format_percent(value)
    unit = "<small>%</small>" if value is not None else ""
    width = 0 if value is None else min(max(value, 0), 100)
    return (
        '<div class="mm-tile">'
        f'<div class="mm-tile__label">{html.escape(label)}</div>'
        f'<div class="mm-tile__value">{shown}{unit}</div>'
        f'<div class="mm-bar"><i class="{bar_class}" style="width:{width:.1f}%"></i></div>'
        "</div>"
    )


def build_report_html(
    *,
    nama: str,
    email: str,
    kelas: str,
    semester: str,
    kuis: float | None,
    kehadiran: float | None,
    passed: bool | None,
    labels: dict[str, str],
    weeks_text: str | None = None,
    note: str | None = None,
) -> str:
    """`passed` None = data belum lengkap (status tidak ditampilkan).

    Semua teks dari sheet di-escape; `labels` dan `weeks_text` sudah terjemahan
    dari lib/i18n.py (`labels`: status_label, status_pass, status_fail, kuis,
    kehadiran).
    """
    esc = html.escape
    who = (
        '<div class="mm-report__who">'
        f'<div class="mm-report__name">{esc(nama)}</div>'
        f'<div class="mm-report__email">{esc(email)}</div>'
        f'<div class="mm-report__meta">{esc(kelas)} · {esc(semester)}</div>'
        "</div>"
    )

    status = ""
    if passed is not None:
        pill_class = "mm-pill--pass" if passed else "mm-pill--fail"
        pill_text = labels["status_pass"] if passed else labels["status_fail"]
        weeks = f'<div class="mm-report__weeks">{esc(weeks_text)}</div>' if weeks_text else ""
        status = (
            '<div class="mm-report__status">'
            f'<div class="mm-report__label">{esc(labels["status_label"])}</div>'
            f'<span class="mm-pill {pill_class}">{esc(pill_text)}</span>'
            f"{weeks}"
            "</div>"
        )

    tiles = (
        '<div class="mm-tiles">'
        + _tile(labels["kuis"], kuis, "mm-bar--blue")
        + _tile(labels["kehadiran"], kehadiran, "mm-bar--green")
        + "</div>"
    )
    note_html = f'<div class="mm-report__note">{esc(note)}</div>' if note else ""
    return f'<div class="mm-report"><div class="mm-report__top">{who}{status}</div>{tiles}{note_html}</div>'
