import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS
from lib.grading import classify
from lib.i18n import t
from lib.report_view import build_report_html

ORG_TAGLINE = "21st Century Training. For Christians. For Free"
ORG_NAME = "Asia Pacific Institute of International Studies · Master of Ministry"

KEY_EMAIL = "lookup_email"
KEY_KELAS = "lookup_kelas"
KEY_REPORT = "student_report"

FIELD_NAMA = "nama"
FIELD_EMAIL = "email"
FIELD_KUIS = "total persentase kuis"
FIELD_KEHADIRAN = "total persentase kehadiran"
FIELD_CATATAN = "catatan"
# Opsional: kalau kedua kolom ini ada di sheet, kartu menampilkan
# "Berdasarkan X dari Y minggu yang tercatat"; kalau tidak, barisnya disembunyikan.
FIELD_MINGGU_TERCATAT = "minggu tercatat"
FIELD_TOTAL_MINGGU = "total minggu"


@st.cache_data(ttl=300, show_spinner=False)
def load_semesters() -> list[str]:
    result = call_apps_script("list_semesters")
    if not result.get("ok"):
        return []
    return result.get("semesters", [])


def normalize_fields(data: dict) -> dict:
    """Petakan header sheet (apa adanya) ke key huruf kecil yang sudah dirapikan."""
    return {str(key).strip().lower(): value for key, value in data.items()}


def parse_percentage(value) -> float | None:
    """Terima angka biasa (75), teks ("75%"), atau pecahan hasil format Percent di
    Google Sheets (0.75) dan kembalikan semuanya dalam skala 0-100."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        num = float(value)
    else:
        text = str(value).strip().replace("%", "").replace(",", ".")
        if not text:
            return None
        try:
            num = float(text)
        except ValueError:
            return None
    return num * 100 if 0 <= num <= 1 else num


def parse_count(value) -> int | None:
    """Bilangan bulat tak-negatif dari sel sheet (angka atau teks), selain itu None."""
    if value is None or value == "":
        return None
    try:
        num = float(str(value).strip().replace(",", "."))
    except ValueError:
        return None
    return int(num) if num >= 0 and num == int(num) else None


def reset_lookup():
    """Kosongkan form dan hasil (tombol "Periksa Status Lain") -- penting di perangkat bersama."""
    st.session_state.pop(KEY_REPORT, None)
    st.session_state[KEY_EMAIL] = ""
    st.session_state[KEY_KELAS] = None


with st.container(key="hero"):
    st.image("assets/logo_apiis.png", width=420)
    st.caption(ORG_TAGLINE)
    st.html(f'<h1 class="mm-title">{t("app_title")} <span>{t("app_title_accent")}</span></h1>')

with st.container(key="card"):
    st.caption(t("intro_caption"))

    try:
        semesters = load_semesters()
    except AppsScriptError as exc:
        # Gangguan jaringan sesaat: tampilkan pesan ramah (hasil gagal tidak di-cache).
        st.error(t(exc.code))
        st.stop()

    if not semesters:
        st.error(t("no_semesters_error"))
        st.stop()

    with st.form("lookup_form", border=False):
        # Key tetap supaya isian form tidak hilang saat ganti bahasa (tanpa key,
        # label yang berubah dianggap widget baru dan isiannya ter-reset).
        email = st.text_input(t("email_label"), placeholder=t("email_placeholder"), key=KEY_EMAIL)
        kelas = st.selectbox(
            t("kelas_label"),
            options=KELAS_OPTIONS,
            index=None,
            placeholder=t("kelas_placeholder"),
            key=KEY_KELAS,
        )
        submitted = st.form_submit_button(
            t("submit_button"), icon=":material/search:", type="primary", width="stretch"
        )

    if submitted:
        st.session_state.pop(KEY_REPORT, None)
        if not email.strip() or not kelas:
            st.warning(t("warning_incomplete"))
        else:
            result = None
            with st.spinner(t("spinner_search")):
                try:
                    result = call_apps_script(
                        "get_report",
                        {
                            "email": email.strip(),
                            "kelas": kelas,
                        },
                    )
                except AppsScriptError as exc:
                    st.error(t(exc.code))

            if result is not None and not result.get("ok"):
                st.error(t("error_not_found"))
            elif result is not None:
                # Hasil disimpan di sesi (bukan hanya dirender sekali) supaya tetap
                # tampil saat halaman dijalankan ulang, mis. ganti bahasa. Teksnya
                # dibangun ulang dari data ini di bawah, jadi ikut berganti bahasa.
                st.session_state[KEY_REPORT] = {
                    "kelas": kelas,
                    "semester": result.get("semester", ""),
                    "data": result.get("data", {}),
                    "typed_email": email.strip(),
                    "rank": result.get("rank"),
                }

    report = st.session_state.get(KEY_REPORT)
    if report:
        semester = report["semester"]
        data = normalize_fields(report["data"])
        nama = data.get(FIELD_NAMA, "-")
        kuis = parse_percentage(data.get(FIELD_KUIS))
        kehadiran = parse_percentage(data.get(FIELD_KEHADIRAN))
        catatan = data.get(FIELD_CATATAN)

        complete = kuis is not None and kehadiran is not None
        status = classify(kuis, kehadiran)

        recorded = parse_count(data.get(FIELD_MINGGU_TERCATAT))
        total = parse_count(data.get(FIELD_TOTAL_MINGGU))
        weeks_text = (
            t("report_weeks", recorded=recorded, total=total)
            if complete and recorded is not None and total
            else None
        )

        rank_info = report.get("rank")
        rank = None
        if isinstance(rank_info, dict):
            position, total_students = parse_count(rank_info.get("position")), parse_count(rank_info.get("total"))
            if position and total_students and position <= total_students:
                rank = (position, total_students)

        st.html(
            build_report_html(
                nama=str(nama or "-"),
                email=str(data.get(FIELD_EMAIL) or report["typed_email"]),
                kelas=report["kelas"],
                semester=semester,
                kuis=kuis,
                kehadiran=kehadiran,
                status=status,
                weeks_text=weeks_text,
                note=t("report_note"),
                rank=rank,
                labels={
                    "status_label": t("report_status_label"),
                    "status_pass": t("report_status_pass"),
                    "status_warn": t("report_status_warn"),
                    "status_fail": t("report_status_fail"),
                    "kuis": t("report_avg_kuis"),
                    "kehadiran": t("report_avg_kehadiran"),
                    "rank": t("report_rank"),
                },
            )
        )
        if not complete:
            st.warning(t("incomplete_data_warning"))

        if catatan:
            st.subheader(t("catatan_subheader"), icon=":material/edit_note:")
            st.write(catatan)

        st.button(t("lookup_another_button"), icon=":material/restart_alt:", on_click=reset_lookup)
    else:
        st.caption(f":material/help: {t('help_not_found')}")

with st.container(key="footer"):
    st.caption(ORG_NAME)
