import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS
from lib.i18n import render_language_switcher, t
from lib.report_view import build_report_html

ORG_TAGLINE = "21st Century Training. For Christians. For Free"

# Syarat kelulusan semester — satu-satunya tempat angka ini didefinisikan.
KEHADIRAN_MIN = 75
KUIS_MIN = 70

KEY_EMAIL = "lookup_email"
KEY_KELAS = "lookup_kelas"
KEY_PHONE = "lookup_phone"
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
    st.session_state[KEY_PHONE] = ""


with st.container(key="hero"):
    st.image("assets/logo_apiis.png", width=420)
    st.caption(ORG_TAGLINE)
    st.title(t("app_title"))

with st.container(key="card"):
    render_language_switcher()

    st.caption(t("intro_caption"))

    semesters = load_semesters()

    if not semesters:
        st.error(t("no_semesters_error"))
        st.stop()

    with st.form("lookup_form", border=True):
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
        phone = st.text_input(t("phone_label"), placeholder=t("phone_placeholder"), key=KEY_PHONE)
        submitted = st.form_submit_button(t("submit_button"), icon=":material/search:")

    if submitted:
        st.session_state.pop(KEY_REPORT, None)
        if not email.strip() or not kelas or not phone.strip():
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
                            "phone": phone.strip(),
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
        passed = (kuis >= KUIS_MIN and kehadiran >= KEHADIRAN_MIN) if complete else None

        recorded = parse_count(data.get(FIELD_MINGGU_TERCATAT))
        total = parse_count(data.get(FIELD_TOTAL_MINGGU))
        weeks_text = (
            t("report_weeks", recorded=recorded, total=total)
            if complete and recorded is not None and total
            else None
        )

        st.html(
            build_report_html(
                nama=str(nama or "-"),
                email=str(data.get(FIELD_EMAIL) or report["typed_email"]),
                kelas=report["kelas"],
                semester=semester,
                kuis=kuis,
                kehadiran=kehadiran,
                passed=passed,
                weeks_text=weeks_text,
                note=t("report_note"),
                labels={
                    "status_label": t("report_status_label"),
                    "status_pass": t("report_status_pass"),
                    "status_fail": t("report_status_fail"),
                    "kuis": t("report_avg_kuis"),
                    "kehadiran": t("report_avg_kehadiran"),
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
    st.caption("MMin Semester Report")
