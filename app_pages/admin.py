import pandas as pd
import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS
from lib.i18n import get_lang, render_language_switcher, t


def is_authed() -> bool:
    return bool(st.session_state.get("admin_authed"))


def show_login():
    with st.container(key="card"):
        render_language_switcher()
        st.subheader(t("admin_login_title"), icon=":material/lock:")
        password = st.text_input(t("admin_password_label"), type="password", key="admin_password_input")
        if st.button(t("admin_login_button"), icon=":material/login:", type="primary"):
            expected = st.secrets.get("admin_password")
            if expected and password == expected:
                st.session_state["admin_authed"] = True
                st.rerun()
            else:
                st.error(t("admin_wrong_password"))


def load_class(kelas: str):
    with st.spinner(t("admin_loading_data")):
        try:
            result = call_apps_script("admin_list_class", {"kelas": kelas})
        except AppsScriptError as exc:
            st.error(t("admin_load_error", code=exc.code))
            return
    if not result.get("ok"):
        st.error(result.get("message", t("admin_load_error_generic")))
        return
    st.session_state["admin_df"] = pd.DataFrame(result.get("rows", []))
    st.session_state["admin_df_kelas"] = kelas
    st.session_state["admin_sheet_name"] = result.get("sheetName", "-")


def render_kelola_nilai():
    kelas = st.selectbox(t("admin_kelas_label"), options=KELAS_OPTIONS, key="admin_kelas")

    if st.button(t("admin_load_button"), icon=":material/refresh:", key="admin_load"):
        load_class(kelas)

    df = st.session_state.get("admin_df")
    loaded_kelas = st.session_state.get("admin_df_kelas")

    if df is None or loaded_kelas != kelas:
        st.info(t("admin_load_hint"))
        return

    st.caption(t("admin_active_tab_caption", sheet=st.session_state.get("admin_sheet_name", "-")))

    uploaded = st.file_uploader(
        t("admin_csv_upload_label"),
        type="csv",
        key="admin_csv",
    )
    if uploaded is not None and st.session_state.get("admin_csv_last_id") != uploaded.file_id:
        try:
            new_df = pd.read_csv(uploaded, dtype=str).fillna("")
        except Exception as exc:  # noqa: BLE001 - tampilkan apa adanya ke admin, bukan siswa
            st.error(t("admin_csv_read_error", err=exc))
        else:
            missing_cols = [c for c in df.columns if c not in new_df.columns]
            extra_cols = [c for c in new_df.columns if c not in df.columns]
            for col in missing_cols:
                new_df[col] = ""
            if missing_cols:
                st.warning(t("admin_csv_missing_cols", cols=", ".join(missing_cols)))
            if extra_cols:
                st.warning(t("admin_csv_extra_cols", cols=", ".join(extra_cols)))
            st.session_state["admin_df"] = new_df[df.columns.tolist()]
            st.session_state["admin_csv_last_id"] = uploaded.file_id
            st.rerun()

    edited_df = st.data_editor(
        st.session_state["admin_df"],
        num_rows="dynamic",
        width="stretch",
        key="admin_data_editor",
    )
    st.caption(t("admin_row_count_caption", n=len(edited_df)))

    confirm = st.checkbox(
        t("admin_confirm_save_label"),
        key="admin_confirm_save",
    )
    if st.button(
        t("admin_save_button"),
        icon=":material/save:",
        type="primary",
        disabled=not confirm,
        key="admin_save_button",
    ):
        rows = edited_df.fillna("").to_dict(orient="records")
        with st.spinner(t("admin_saving_spinner")):
            try:
                save_result = call_apps_script("admin_save_class", {"kelas": kelas, "rows": rows})
            except AppsScriptError as exc:
                st.error(t("admin_save_error", code=exc.code))
                save_result = None
        if save_result and save_result.get("ok"):
            st.success(t("admin_save_success", n=save_result.get("savedRows", 0)))
            st.session_state["admin_df"] = edited_df
        elif save_result:
            st.error(save_result.get("message", t("admin_save_error_generic")))


def render_log_akses():
    if st.button(t("admin_load_log_button"), icon=":material/refresh:", key="admin_load_log"):
        with st.spinner(t("admin_loading_log")):
            try:
                result = call_apps_script("admin_access_log")
            except AppsScriptError as exc:
                st.error(t("admin_log_load_error", code=exc.code))
                result = None
        if result and result.get("ok"):
            st.session_state["admin_log_rows"] = result.get("rows", [])
        elif result:
            st.error(result.get("message", t("admin_log_load_error_generic")))

    log_rows = st.session_state.get("admin_log_rows")
    if log_rows is None:
        st.info(t("admin_log_hint"))
        return

    log_df = pd.DataFrame(log_rows)
    if log_df.empty:
        st.info(t("admin_log_empty"))
        return

    log_df["Timestamp"] = pd.to_datetime(log_df["Timestamp"], errors="coerce")

    summary = (
        log_df.groupby(["Nama", "Email", "Kelas"], as_index=False)
        .agg(**{
            t("admin_col_jumlah_akses"): ("Timestamp", "count"),
            t("admin_col_terakhir_diakses"): ("Timestamp", "max"),
        })
        .sort_values(t("admin_col_terakhir_diakses"), ascending=False)
    )

    # Key disertai kode bahasa: BaseWeb Select menyimpan label lama secara
    # cache di sisi klien kalau nilai (value) tidak berubah, jadi teks yang
    # tampil di kotak tertutup bisa "nyangkut" dalam bahasa sebelumnya sampai
    # widget-nya di-remount. Menambahkan bahasa ke key memaksa remount itu.
    kelas_filter = st.selectbox(
        t("admin_filter_kelas_label"),
        options=["__all__"] + KELAS_OPTIONS,
        format_func=lambda k: t("admin_filter_all") if k == "__all__" else k,
        key=f"admin_log_kelas_filter_{get_lang()}",
    )
    if kelas_filter != "__all__":
        summary = summary[summary["Kelas"] == kelas_filter]

    st.subheader(t("admin_summary_subheader"), icon=":material/bar_chart:")
    # Key disertai bahasa: sama seperti selectbox di atas, glide-data-grid
    # bisa mempertahankan header lama secara visual kalau hanya nama kolom
    # yang berubah tanpa remount.
    st.dataframe(summary, hide_index=True, width="stretch", key=f"admin_log_summary_{get_lang()}")

    with st.expander(t("admin_raw_log_expander")):
        st.dataframe(
            log_df.sort_values("Timestamp", ascending=False),
            hide_index=True,
            width="stretch",
        )

    st.subheader(t("admin_missing_subheader"), icon=":material/report:")
    if st.button(t("admin_check_now_button"), icon=":material/search:", key="admin_check_missing"):
        accessed_emails = set(log_df["Email"].astype(str).str.strip().str.lower())
        missing = []
        with st.spinner(t("admin_comparing_spinner")):
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
            st.warning(t("admin_missing_warning", n=len(missing)))
            st.dataframe(pd.DataFrame(missing), hide_index=True, width="stretch")
        else:
            st.success(t("admin_missing_none"))


with st.container(key="hero"):
    st.image("assets/logo_apiis.png", width=420)
    st.title(t("admin_page_title"))

if not is_authed():
    show_login()
    st.stop()

with st.container(key="card"):
    render_language_switcher()

    header_col, logout_col = st.columns([3, 1])
    header_col.caption(t("admin_signed_in_caption"))
    if logout_col.button(t("admin_logout_button"), icon=":material/logout:"):
        st.session_state.pop("admin_authed", None)
        st.rerun()

    tab_nilai, tab_log = st.tabs([t("admin_tab_kelola"), t("admin_tab_log")])
    with tab_nilai:
        render_kelola_nilai()
    with tab_log:
        render_log_akses()
