import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script

st.set_page_config(
    page_title="MMin Semester Report",
    page_icon=":material/school:",
    layout="centered",
)

KELAS_OPTIONS = ["MMin 2 Leadership", "MMin 2 Pastoral"]

# Kolom-kolom ini dikenali dari nama header di Google Sheets (tidak case-sensitive)
# untuk dikelompokkan secara khusus; sisanya ditampilkan sebagai nilai mata pelajaran.
RESERVED_COLUMNS = {"kelas", "nomor hp", "nama"}
ATTENDANCE_HINTS = ("kehadiran", "hadir", "presensi")
NOTE_HINTS = ("catatan",)


@st.cache_data(ttl=300, show_spinner=False)
def load_semesters() -> list[str]:
    result = call_apps_script("list_semesters")
    if not result.get("ok"):
        return []
    return result.get("semesters", [])


def split_columns(data: dict) -> tuple[dict, dict, dict]:
    nilai, kehadiran, catatan = {}, {}, {}
    for key, value in data.items():
        lower = key.strip().lower()
        if lower in RESERVED_COLUMNS:
            continue
        if any(hint in lower for hint in ATTENDANCE_HINTS):
            kehadiran[key] = value
        elif any(hint in lower for hint in NOTE_HINTS):
            catatan[key] = value
        else:
            nilai[key] = value
    return nilai, kehadiran, catatan


st.title("Laporan semester MMin", icon=":material/school:")
st.caption(
    "Masukkan kelas dan nomor HP yang terdaftar saat pendaftaran program untuk melihat "
    "nilai dan kehadiran Anda."
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

    data = result.get("data", {})
    nama = data.get("Nama", "-")
    nilai, kehadiran, catatan = split_columns(data)

    st.success(f"Ditemukan laporan untuk **{nama}** — {kelas}, {semester}")

    if nilai:
        st.subheader("Nilai", icon=":material/grade:")
        st.dataframe(
            {"Mata pelajaran": list(nilai.keys()), "Nilai": list(nilai.values())},
            hide_index=True,
            width="stretch",
        )

    if kehadiran:
        st.subheader("Kehadiran", icon=":material/event_available:")
        cols = st.columns(len(kehadiran))
        for col, (label, value) in zip(cols, kehadiran.items()):
            col.metric(label, value)

    if catatan:
        st.subheader("Catatan wali kelas", icon=":material/edit_note:")
        for label, value in catatan.items():
            if value:
                st.write(value)
