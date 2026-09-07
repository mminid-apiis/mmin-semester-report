import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script

st.set_page_config(
    page_title="MMin Semester Report",
    page_icon=":material/school:",
    layout="centered",
)

KELAS_OPTIONS = ["MMin 2 Leadership", "MMin 2 Pastoral"]

# Syarat kelulusan semester — satu-satunya tempat angka ini didefinisikan.
KEHADIRAN_MIN = 75
KUIS_MIN = 70

FIELD_EMAIL = "email"
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


st.title("Laporan semester MMin", icon=":material/school:")
st.caption(
    "Masukkan kelas dan nomor HP yang terdaftar saat pendaftaran program untuk melihat "
    "nilai dan kehadiran Anda."
)
st.caption(
    f"Syarat kelulusan semester: kehadiran Kelas Zoom minimal {KEHADIRAN_MIN}% dan "
    f"total nilai kuis minimal {KUIS_MIN}%."
)

semesters = load_semesters()

if not semesters:
    st.error("Laporan belum tersedia saat ini. Hubungi wali kelas Anda.")
    st.stop()

with st.form("lookup_form", border=True):
    semester = st.selectbox("Semester", options=semesters, index=len(semesters) - 1)
    kelas = st.selectbox(
        "Kelas", options=KELAS_OPTIONS, index=None, placeholder="Pilih kelas Anda"
    )
    phone = st.text_input("Nomor HP", placeholder="08xxxxxxxxxx")
    submitted = st.form_submit_button("Lihat laporan", icon=":material/search:")

if submitted:
    if not kelas or not phone.strip():
        st.warning("Lengkapi kelas dan nomor HP terlebih dahulu.")
        st.stop()

    with st.spinner("Mencari data..."):
        try:
            result = call_apps_script(
                "get_report",
                {"kelas": kelas, "phone": phone.strip(), "semester": semester},
            )
        except AppsScriptError as exc:
            st.error(str(exc))
            st.stop()

    if not result.get("ok"):
        st.error(
            "Data tidak ditemukan. Pastikan kelas dan nomor HP sesuai dengan data "
            "pendaftaran Anda."
        )
        st.stop()

    data = normalize_fields(result.get("data", {}))
    nama = data.get(FIELD_NAMA, "-")
    email = data.get(FIELD_EMAIL)
    kuis = parse_percentage(data.get(FIELD_KUIS))
    kehadiran = parse_percentage(data.get(FIELD_KEHADIRAN))
    catatan = data.get(FIELD_CATATAN)

    st.success(f"Ditemukan laporan untuk **{nama}** — {kelas}, {semester}")
    if email:
        st.caption(f"Terdaftar dengan email {email}")

    col1, col2 = st.columns(2)
    col1.metric("Total persentase kuis", f"{kuis:.0f}%" if kuis is not None else "-")
    col2.metric("Total persentase kehadiran", f"{kehadiran:.0f}%" if kehadiran is not None else "-")

    st.subheader("Status kelulusan semester", icon=":material/verified:")
    if kuis is None or kehadiran is None:
        st.warning("Data belum lengkap untuk menentukan status kelulusan. Hubungi wali kelas Anda.")
    else:
        kuis_ok = kuis >= KUIS_MIN
        kehadiran_ok = kehadiran >= KEHADIRAN_MIN
        kehadiran_line = (
            f"Kehadiran Zoom: {kehadiran:.0f}% (memenuhi syarat)"
            if kehadiran_ok
            else f"Kehadiran Zoom: {kehadiran:.0f}% (syarat minimal {KEHADIRAN_MIN}%)"
        )
        kuis_line = (
            f"Total kuis: {kuis:.0f}% (memenuhi syarat)"
            if kuis_ok
            else f"Total kuis: {kuis:.0f}% (syarat minimal {KUIS_MIN}%)"
        )
        if kuis_ok and kehadiran_ok:
            st.success(
                f"Memenuhi syarat kelulusan {semester}", icon=":material/check_circle:"
            )
        else:
            st.error(
                f"Belum memenuhi syarat kelulusan {semester}\n\n"
                f"- {kehadiran_line}\n"
                f"- {kuis_line}",
                icon=":material/cancel:",
            )

    if catatan:
        st.subheader("Catatan wali kelas", icon=":material/edit_note:")
        st.write(catatan)
