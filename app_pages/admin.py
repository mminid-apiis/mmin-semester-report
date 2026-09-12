import pandas as pd
import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS


def is_authed() -> bool:
    return bool(st.session_state.get("admin_authed"))


def show_login():
    with st.container(key="card"):
        st.subheader("Masuk sebagai admin", icon=":material/lock:")
        password = st.text_input("Password admin", type="password", key="admin_password_input")
        if st.button("Masuk", icon=":material/login:", type="primary"):
            expected = st.secrets.get("admin_password")
            if expected and password == expected:
                st.session_state["admin_authed"] = True
                st.rerun()
            else:
                st.error("Password salah.")


def load_class(kelas: str):
    with st.spinner("Memuat data..."):
        try:
            result = call_apps_script("admin_list_class", {"kelas": kelas})
        except AppsScriptError as exc:
            st.error(f"Gagal memuat data ({exc.code}).")
            return
    if not result.get("ok"):
        st.error(result.get("message", "Gagal memuat data."))
        return
    st.session_state["admin_df"] = pd.DataFrame(result.get("rows", []))
    st.session_state["admin_df_kelas"] = kelas
    st.session_state["admin_sheet_name"] = result.get("sheetName", "-")


def render_kelola_nilai():
    kelas = st.selectbox("Pilih kelas", options=KELAS_OPTIONS, key="admin_kelas")

    if st.button("Muat data dari Google Sheets", icon=":material/refresh:", key="admin_load"):
        load_class(kelas)

    df = st.session_state.get("admin_df")
    loaded_kelas = st.session_state.get("admin_df_kelas")

    if df is None or loaded_kelas != kelas:
        st.info("Klik \"Muat data dari Google Sheets\" untuk mulai mengelola nilai kelas ini.")
        return

    st.caption(f"Tab aktif: **{st.session_state.get('admin_sheet_name', '-')}**")

    uploaded = st.file_uploader(
        "Atau unggah CSV untuk mengisi tabel di bawah sekaligus",
        type="csv",
        key="admin_csv",
    )
    if uploaded is not None and st.session_state.get("admin_csv_last_id") != uploaded.file_id:
        try:
            new_df = pd.read_csv(uploaded, dtype=str).fillna("")
        except Exception as exc:  # noqa: BLE001 - tampilkan apa adanya ke admin, bukan siswa
            st.error(f"Gagal membaca CSV: {exc}")
        else:
            missing_cols = [c for c in df.columns if c not in new_df.columns]
            extra_cols = [c for c in new_df.columns if c not in df.columns]
            for col in missing_cols:
                new_df[col] = ""
            if missing_cols:
                st.warning(f"Kolom CSV tidak lengkap, dikosongkan: {', '.join(missing_cols)}")
            if extra_cols:
                st.warning(f"Kolom CSV ini diabaikan (tidak ada di sheet): {', '.join(extra_cols)}")
            st.session_state["admin_df"] = new_df[df.columns.tolist()]
            st.session_state["admin_csv_last_id"] = uploaded.file_id
            st.rerun()

    edited_df = st.data_editor(
        st.session_state["admin_df"],
        num_rows="dynamic",
        width="stretch",
        key="admin_data_editor",
    )
    st.caption(f"{len(edited_df)} baris siswa.")

    confirm = st.checkbox(
        "Saya yakin ingin menyimpan perubahan ini ke Google Sheets (menimpa data lama di tab ini).",
        key="admin_confirm_save",
    )
    if st.button(
        "Simpan ke Google Sheets",
        icon=":material/save:",
        type="primary",
        disabled=not confirm,
        key="admin_save_button",
    ):
        rows = edited_df.fillna("").to_dict(orient="records")
        with st.spinner("Menyimpan..."):
            try:
                save_result = call_apps_script("admin_save_class", {"kelas": kelas, "rows": rows})
            except AppsScriptError as exc:
                st.error(f"Gagal menyimpan ({exc.code}).")
                save_result = None
        if save_result and save_result.get("ok"):
            st.success(f"Tersimpan {save_result.get('savedRows', 0)} baris ke Google Sheets.")
            st.session_state["admin_df"] = edited_df
        elif save_result:
            st.error(save_result.get("message", "Gagal menyimpan."))


def render_log_akses():
    if st.button("Muat log akses", icon=":material/refresh:", key="admin_load_log"):
        with st.spinner("Memuat log akses..."):
            try:
                result = call_apps_script("admin_access_log")
            except AppsScriptError as exc:
                st.error(f"Gagal memuat log ({exc.code}).")
                result = None
        if result and result.get("ok"):
            st.session_state["admin_log_rows"] = result.get("rows", [])
        elif result:
            st.error(result.get("message", "Gagal memuat log."))

    log_rows = st.session_state.get("admin_log_rows")
    if log_rows is None:
        st.info("Klik \"Muat log akses\" untuk melihat riwayat akses siswa.")
        return

    log_df = pd.DataFrame(log_rows)
    if log_df.empty:
        st.info("Belum ada catatan akses siswa.")
        return

    log_df["Timestamp"] = pd.to_datetime(log_df["Timestamp"], errors="coerce")

    summary = (
        log_df.groupby(["Nama", "Email", "Kelas"], as_index=False)
        .agg(**{"Jumlah Akses": ("Timestamp", "count"), "Terakhir Diakses": ("Timestamp", "max")})
        .sort_values("Terakhir Diakses", ascending=False)
    )

    kelas_filter = st.selectbox(
        "Filter kelas", options=["Semua kelas"] + KELAS_OPTIONS, key="admin_log_kelas_filter"
    )
    if kelas_filter != "Semua kelas":
        summary = summary[summary["Kelas"] == kelas_filter]

    st.subheader("Ringkasan per siswa", icon=":material/bar_chart:")
    st.dataframe(summary, hide_index=True, width="stretch")

    with st.expander("Lihat semua catatan akses (mentah)"):
        st.dataframe(
            log_df.sort_values("Timestamp", ascending=False),
            hide_index=True,
            width="stretch",
        )

    st.subheader("Siswa yang belum pernah membuka laporannya", icon=":material/report:")
    if st.button("Cek sekarang", icon=":material/search:", key="admin_check_missing"):
        accessed_emails = set(log_df["Email"].astype(str).str.strip().str.lower())
        missing = []
        with st.spinner("Membandingkan dengan daftar siswa..."):
            for kelas_opt in KELAS_OPTIONS:
                try:
                    roster_result = call_apps_script("admin_list_class", {"kelas": kelas_opt})
                except AppsScriptError:
                    continue
                if not roster_result.get("ok"):
                    continue
                for row in roster_result.get("rows", []):
                    row_email = str(row.get("Email", "")).strip().lower()
                    if row_email and row_email not in accessed_emails:
                        missing.append(
                            {"Nama": row.get("Nama", ""), "Email": row.get("Email", ""), "Kelas": kelas_opt}
                        )
        if missing:
            st.warning(f"{len(missing)} siswa belum pernah membuka laporan mereka:")
            st.dataframe(pd.DataFrame(missing), hide_index=True, width="stretch")
        else:
            st.success("Semua siswa (yang datanya ada di sheet) pernah membuka laporan mereka.")


with st.container(key="hero"):
    st.image("assets/logo_apiis.png")
    st.title("Admin Panel")

if not is_authed():
    show_login()
    st.stop()

with st.container(key="card"):
    header_col, logout_col = st.columns([3, 1])
    header_col.caption("Masuk sebagai admin")
    if logout_col.button("Keluar", icon=":material/logout:"):
        st.session_state.pop("admin_authed", None)
        st.rerun()

    tab_nilai, tab_log = st.tabs(["Kelola Nilai", "Log Akses Siswa"])
    with tab_nilai:
        render_kelola_nilai()
    with tab_log:
        render_log_akses()
