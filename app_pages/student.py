import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS
from lib.i18n import LANGUAGES, get_lang, t

ORG_TAGLINE = "21st Century Training. For Christians. For Free"

# Syarat kelulusan semester — satu-satunya tempat angka ini didefinisikan.
KEHADIRAN_MIN = 75
KUIS_MIN = 70

FIELD_NAMA = "nama"
FIELD_KUIS = "total persentase kuis"
FIELD_KEHADIRAN = "total persentase kehadiran"
FIELD_CATATAN = "catatan"


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


with st.container(key="hero"):
    st.image("assets/logo_apiis.png")
    st.caption(ORG_TAGLINE)
    st.title(t("app_title"))

with st.container(key="card"):
    lang_codes = list(LANGUAGES.keys())
    st.selectbox(
        t("lang_label"),
        options=lang_codes,
        format_func=lambda code: LANGUAGES[code],
        index=lang_codes.index(get_lang()),
        key="lang",
    )

    st.caption(t("intro_caption"))
    st.caption(t("criteria_caption", kehadiran_min=KEHADIRAN_MIN, kuis_min=KUIS_MIN))

    semesters = load_semesters()

    if not semesters:
        st.error(t("no_semesters_error"))
        st.stop()

    with st.form("lookup_form", border=True):
        email = st.text_input(t("email_label"), placeholder=t("email_placeholder"))
        kelas = st.selectbox(
            t("kelas_label"), options=KELAS_OPTIONS, index=None, placeholder=t("kelas_placeholder")
        )
        phone = st.text_input(t("phone_label"), placeholder=t("phone_placeholder"))
        submitted = st.form_submit_button(t("submit_button"), icon=":material/search:")

    if submitted:
        if not email.strip() or not kelas or not phone.strip():
            st.warning(t("warning_incomplete"))
            st.stop()

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
                st.stop()

        if not result.get("ok"):
            st.error(t("error_not_found"))
            st.stop()

        semester = result.get("semester", "")
        data = normalize_fields(result.get("data", {}))
        nama = data.get(FIELD_NAMA, "-")
        kuis = parse_percentage(data.get(FIELD_KUIS))
        kehadiran = parse_percentage(data.get(FIELD_KEHADIRAN))
        catatan = data.get(FIELD_CATATAN)

        st.success(t("success_found", nama=nama, kelas=kelas, semester=semester))

        col1, col2 = st.columns(2)
        col1.metric(t("metric_kuis"), f"{kuis:.0f}%" if kuis is not None else "-")
        col2.metric(t("metric_kehadiran"), f"{kehadiran:.0f}%" if kehadiran is not None else "-")

        st.subheader(t("status_subheader"), icon=":material/verified:")
        if kuis is None or kehadiran is None:
            st.warning(t("incomplete_data_warning"))
        else:
            kuis_ok = kuis >= KUIS_MIN
            kehadiran_ok = kehadiran >= KEHADIRAN_MIN
            kehadiran_line = t(
                "line_kehadiran_ok" if kehadiran_ok else "line_kehadiran_fail",
                v=kehadiran,
                min=KEHADIRAN_MIN,
            )
            kuis_line = t(
                "line_kuis_ok" if kuis_ok else "line_kuis_fail",
                v=kuis,
                min=KUIS_MIN,
            )
            if kuis_ok and kehadiran_ok:
                st.success(t("status_pass", semester=semester), icon=":material/check_circle:")
            else:
                st.error(
                    f"{t('status_fail', semester=semester)}\n\n- {kehadiran_line}\n- {kuis_line}",
                    icon=":material/cancel:",
                )

        if catatan:
            st.subheader(t("catatan_subheader"), icon=":material/edit_note:")
            st.write(catatan)

with st.container(key="footer"):
    st.caption("MMin Semester Report")
