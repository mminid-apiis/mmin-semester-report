import math
from collections import Counter

import pandas as pd
import streamlit as st

from lib import admin_auth
from lib.apps_script_client import AppsScriptError, call_apps_script
from lib.constants import KELAS_OPTIONS
from lib.i18n import get_lang, render_language_switcher, t

NOTIFY_JENIS = ["baru", "pengingat"]
DEFAULT_NOTIFY_BATCH = 30


def action_label(code: str) -> str:
    label = t(f"admin_action_{code}")
    return code if label == f"admin_action_{code}" else label


def show_login():
    accounts = admin_auth.get_accounts()
    with st.container(key="card"):
        render_language_switcher()
        st.subheader(t("admin_login_title"), icon=":material/lock:")
        if not accounts:
            st.error(t("admin_no_accounts"))
            return

        notice = st.empty()
        locked = admin_auth.seconds_locked()
        if locked:
            notice.error(t("admin_locked", seconds=locked))

        with st.form("admin_login_form"):
            username = st.selectbox(t("admin_account_label"), options=list(accounts))
            password = st.text_input(t("admin_password_label"), type="password")
            submitted = st.form_submit_button(
                t("admin_login_button"), icon=":material/login:", type="primary"
            )

        if submitted:
            status = admin_auth.attempt_login(username, password)
            if status in (admin_auth.LOGIN_OK, admin_auth.LOGIN_OK_LOG_FAILED):
                if status == admin_auth.LOGIN_OK_LOG_FAILED:
                    st.session_state["admin_log_warning"] = True
                st.rerun()
            remaining = admin_auth.seconds_locked()
            if remaining:
                notice.error(t("admin_locked", seconds=remaining))
            else:
                notice.error(t("admin_wrong_credentials"))


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
    st.session_state["admin_version"] = result.get("version")
    bump_editor_nonce()


def bump_editor_nonce():
    # Key baru = data_editor mulai dari nol, supaya sisa suntingan lama (mis. baris
    # yang dihapus) tidak diterapkan ulang ke data yang baru dimuat/disimpan.
    st.session_state["admin_editor_nonce"] = st.session_state.get("admin_editor_nonce", 0) + 1


def render_kelola_nilai(admin: str):
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
            bump_editor_nonce()
            st.rerun()

    edited_df = st.data_editor(
        st.session_state["admin_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"admin_data_editor_{st.session_state.get('admin_editor_nonce', 0)}",
    )
    st.caption(t("admin_row_count_caption", n=len(edited_df)))

    confirm = st.checkbox(
        t("admin_confirm_save_label"),
        key=f"admin_confirm_save_{st.session_state.get('admin_editor_nonce', 0)}",
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
                save_result = call_apps_script(
                    "admin_save_class",
                    {
                        "kelas": kelas,
                        "rows": rows,
                        "admin": admin,
                        "baseVersion": st.session_state.get("admin_version"),
                    },
                )
            except AppsScriptError as exc:
                st.error(t("admin_save_error", code=exc.code))
                save_result = None
        if save_result and save_result.get("ok"):
            changes = save_result.get("changes") or {}
            st.success(
                t(
                    "admin_save_success",
                    n=save_result.get("savedRows", 0),
                    ubah=changes.get("ubah", 0),
                    tambah=changes.get("tambah", 0),
                    hapus=changes.get("hapus", 0),
                )
            )
            st.session_state["admin_df"] = edited_df
            st.session_state["admin_version"] = save_result.get("version")
            bump_editor_nonce()
        elif save_result and save_result.get("code") == "conflict":
            st.error(t("admin_save_conflict"))
            st.download_button(
                t("admin_save_conflict_download"),
                data=edited_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{kelas.replace(' ', '_')}.csv",
                mime="text/csv",
                icon=":material/download:",
                on_click="ignore",
            )
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


def load_notify_status(kelas: str):
    with st.spinner(t("admin_notify_loading")):
        try:
            result = call_apps_script("admin_notify_status", {"kelas": kelas})
        except AppsScriptError as exc:
            st.error(t("admin_notify_load_error", code=exc.code))
            return
    if not result.get("ok"):
        st.error(result.get("message", t("admin_notify_load_error_generic")))
        return
    result["kelas"] = kelas
    st.session_state["admin_notify_status"] = result


def run_notify_send(kelas: str, jenis: str, force: bool, total: int, batch_size: int, admin: str):
    """Kirim batch demi batch sampai habis; hasil disimpan lalu halaman di-rerun."""
    progress = st.progress(0.0, text=t("admin_notify_sending", done=0, total=total))
    sent_total = 0
    failed: list[str] = []
    notice: tuple[str, str] | None = None

    for _ in range(math.ceil(total / max(batch_size, 1)) + 5):
        try:
            res = call_apps_script(
                "admin_notify_send",
                {"kelas": kelas, "jenis": jenis, "admin": admin, "force": force, "exclude": failed},
                timeout=120,
            )
        except AppsScriptError as exc:
            notice = ("error", t("admin_notify_send_error", code=exc.code))
            break
        if not res.get("ok"):
            if res.get("code") == "quota":
                notice = ("warning", t("admin_notify_quota_exhausted"))
            else:
                notice = ("error", res.get("message") or t("admin_notify_send_error_generic"))
            break

        sent_now = int(res.get("sent", 0))
        failed_now = list(res.get("failed", []))
        sent_total += sent_now
        failed += failed_now
        done = sent_total + len(failed)
        progress.progress(
            min(1.0, done / total) if total else 1.0,
            text=t("admin_notify_sending", done=done, total=total),
        )
        if int(res.get("remaining", 0)) == 0 or sent_now + len(failed_now) == 0:
            break

    st.session_state["admin_notify_result"] = {
        "sent": sent_total,
        "failed": failed,
        "notice": notice,
    }
    st.session_state["admin_notify_nonce"] = st.session_state.get("admin_notify_nonce", 0) + 1
    load_notify_status(kelas)
    st.rerun()


def render_notifikasi(admin: str):
    st.caption(t("admin_notify_intro"))

    result = st.session_state.pop("admin_notify_result", None)
    if result:
        if result["sent"] or not result["notice"]:
            st.success(t("admin_notify_done", sent=result["sent"]))
        if result["failed"]:
            st.warning(
                t("admin_notify_done_failed", n=len(result["failed"]), emails=", ".join(result["failed"]))
            )
        if result["notice"]:
            level, message = result["notice"]
            getattr(st, level)(message)

    kelas = st.selectbox(t("admin_kelas_label"), options=KELAS_OPTIONS, key="admin_notify_kelas")
    if st.button(t("admin_notify_load_button"), icon=":material/refresh:", key="admin_notify_load"):
        load_notify_status(kelas)

    status = st.session_state.get("admin_notify_status")
    if not status or status.get("kelas") != kelas:
        st.info(t("admin_notify_hint"))
        return

    quota = int(status.get("quota", 0))
    invalid_names = status.get("invalidNames", [])
    st.caption(
        t("admin_notify_active_tab_caption", sheet=status.get("sheetName", "-"), semester=status.get("semester", "-"))
    )
    col_quota, col_students, col_invalid = st.columns(3)
    col_quota.metric(t("admin_notify_metric_quota"), quota)
    col_students.metric(t("admin_notify_metric_students"), status.get("totalStudents", 0))
    col_invalid.metric(t("admin_notify_metric_invalid"), len(invalid_names))
    if invalid_names:
        with st.expander(t("admin_notify_invalid_expander")):
            st.write(", ".join(invalid_names))

    # Key disertai bahasa (lihat catatan di render_log_akses): label tombol
    # bergantung bahasa lewat format_func. Pilihan disimpan terpisah supaya tidak
    # hilang saat widget di-remount karena ganti bahasa.
    jenis = st.segmented_control(
        t("admin_notify_jenis_label"),
        options=NOTIFY_JENIS,
        format_func=lambda j: t(f"admin_notify_jenis_{j}"),
        default=st.session_state.get("admin_notify_jenis_value", NOTIFY_JENIS[0]),
        required=True,
        key=f"admin_notify_jenis_{get_lang()}",
    )
    st.session_state["admin_notify_jenis_value"] = jenis
    force = st.checkbox(t("admin_notify_force_label"), key="admin_notify_force")

    plan = status["plans"][jenis]
    eligible = list(plan["eligible"])
    skipped = list(plan["skipped"])
    if force:
        # Sama dengan perilaku server saat force: hanya "sudah membuka" yang tetap dilewati.
        eligible += [{"nama": s["nama"], "email": s["email"]} for s in skipped if s["reason"] != "sudah_membuka"]
        skipped = [s for s in skipped if s["reason"] == "sudah_membuka"]

    if eligible:
        st.markdown(t("admin_notify_plan_summary", n=len(eligible)))
    else:
        st.info(t("admin_notify_nothing"))
    if skipped:
        counts = Counter(s["reason"] for s in skipped)
        parts = ", ".join(f"{t(f'admin_notify_reason_{reason}')} ({n})" for reason, n in counts.items())
        st.caption(t("admin_notify_skipped_summary", parts=parts))

    if eligible:
        with st.expander(t("admin_notify_recipients_expander")):
            st.dataframe(
                pd.DataFrame([{"Nama": s["nama"], "Email": s["email"]} for s in eligible]),
                hide_index=True,
                width="stretch",
            )
    if skipped:
        with st.expander(t("admin_notify_skipped_expander")):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Nama": s["nama"],
                            "Email": s["email"],
                            t("admin_col_alasan"): t(f"admin_notify_reason_{s['reason']}"),
                        }
                        for s in skipped
                    ]
                ),
                hide_index=True,
                width="stretch",
                key=f"admin_notify_skipped_{get_lang()}",
            )

    mail = status["previews"][jenis]
    with st.expander(t("admin_notify_preview_expander")):
        st.caption(t("admin_notify_preview_note"))
        st.markdown(f"**{t('admin_notify_preview_subject', subject=mail['subject'])}**")
        st.text(mail["body"])

    if st.button(
        t("admin_notify_test_button", owner=status.get("ownerEmail") or "-"),
        icon=":material/mark_email_read:",
        key="admin_notify_test",
    ):
        with st.spinner(t("admin_notify_test_spinner")):
            try:
                test_result = call_apps_script(
                    "admin_notify_test", {"kelas": kelas, "jenis": jenis, "admin": admin}, timeout=60
                )
            except AppsScriptError as exc:
                st.error(t("admin_notify_test_error", code=exc.code))
                test_result = None
        if test_result and test_result.get("ok"):
            st.success(t("admin_notify_test_ok", to=test_result.get("to", "")))
        elif test_result:
            st.error(test_result.get("message") or t("admin_notify_test_error", code="-"))

    if quota <= 0:
        st.error(t("admin_notify_quota_exhausted"))
    elif eligible and quota < len(eligible):
        st.warning(t("admin_notify_quota_low", quota=quota, n=len(eligible)))

    # Key memuat jenis, force, dan jumlah penerima: centang konfirmasi otomatis
    # hilang kalau daftar penerimanya berubah, jadi tidak bisa "terlanjur" setuju.
    nonce = st.session_state.get("admin_notify_nonce", 0)
    confirmed = st.checkbox(
        t("admin_notify_confirm", n=len(eligible), kelas=kelas),
        key=f"admin_notify_confirm_{kelas}_{jenis}_{int(force)}_{len(eligible)}_{nonce}",
        disabled=not eligible or quota <= 0,
    )
    if st.button(
        t("admin_notify_send_button", n=len(eligible)),
        icon=":material/send:",
        type="primary",
        disabled=not (confirmed and eligible and quota > 0),
        key="admin_notify_send",
    ):
        run_notify_send(
            kelas, jenis, force, len(eligible), int(status.get("batchSize", DEFAULT_NOTIFY_BATCH)), admin
        )

    history = status.get("history") or []
    if history:
        st.subheader(t("admin_notify_history_subheader"), icon=":material/history:")
        history_df = pd.DataFrame(history).astype(str)
        shown = [c for c in ("Timestamp", "Admin", "Email", "Jenis", "Status") if c in history_df.columns]
        st.dataframe(history_df[shown], hide_index=True, width="stretch")


def render_audit_log():
    if st.button(t("admin_audit_load_button"), icon=":material/refresh:", key="admin_load_audit"):
        with st.spinner(t("admin_audit_loading")):
            try:
                result = call_apps_script("admin_audit_log")
            except AppsScriptError as exc:
                st.error(t("admin_audit_load_error", code=exc.code))
                result = None
        if result and result.get("ok"):
            st.session_state["admin_audit_rows"] = result.get("rows", [])
        elif result:
            st.error(result.get("message", t("admin_audit_load_error_generic")))

    audit_rows = st.session_state.get("admin_audit_rows")
    if audit_rows is None:
        st.info(t("admin_audit_hint"))
        return
    if not audit_rows:
        st.info(t("admin_audit_empty"))
        return

    # Semua kolom dijadikan teks: kolom Nilai Lama/Baru bercampur angka & teks,
    # dan Streamlit/Arrow tidak suka kolom bertipe campuran.
    audit_df = pd.DataFrame(audit_rows).astype(str)
    admins = sorted(audit_df["Admin"].unique())

    st.subheader(t("admin_audit_login_subheader"), icon=":material/login:")
    login_summary = []
    for name in admins:
        mine = audit_df[audit_df["Admin"] == name]
        logins = mine[mine["Aksi"] == "login"]
        login_summary.append({
            t("admin_col_admin"): name,
            t("admin_col_jumlah_login"): len(logins),
            t("admin_col_login_terakhir"): logins["Timestamp"].max() if len(logins) else "-",
            t("admin_col_login_gagal"): int((mine["Aksi"] == "login_gagal").sum()),
        })
    # Key disertai bahasa: nama kolom bergantung bahasa (lihat render_log_akses).
    st.dataframe(
        pd.DataFrame(login_summary),
        hide_index=True,
        width="stretch",
        key=f"admin_audit_login_summary_{get_lang()}",
    )

    admin_filter = st.selectbox(
        t("admin_audit_filter_admin"),
        options=["__all__"] + admins,
        format_func=lambda a: t("admin_audit_filter_all") if a == "__all__" else a,
        key=f"admin_audit_filter_admin_{get_lang()}",
    )
    aksi_options = sorted(audit_df["Aksi"].unique())
    aksi_filter = st.multiselect(
        t("admin_audit_filter_aksi"),
        options=aksi_options,
        format_func=action_label,
        key=f"admin_audit_filter_aksi_{get_lang()}",
    )

    view = audit_df
    if admin_filter != "__all__":
        view = view[view["Admin"] == admin_filter]
    if aksi_filter:
        view = view[view["Aksi"].isin(aksi_filter)]
    view = view.sort_values("Timestamp", ascending=False, kind="stable").copy()
    view["Aksi"] = view["Aksi"].map(action_label)

    st.subheader(t("admin_audit_all_subheader"), icon=":material/history:")
    st.dataframe(view, hide_index=True, width="stretch", key=f"admin_audit_all_{get_lang()}")


with st.container(key="hero"):
    st.image("assets/logo_apiis.png", width=420)
    st.title(t("admin_page_title"))

admin_user = admin_auth.current_admin()
if admin_user is None:
    show_login()
    st.stop()

with st.container(key="card"):
    render_language_switcher()

    if st.session_state.pop("admin_log_warning", False):
        st.warning(t("admin_log_warning"))

    header_col, logout_col = st.columns([3, 1])
    header_col.caption(t("admin_signed_in_as", user=admin_user))
    if logout_col.button(t("admin_logout_button"), icon=":material/logout:"):
        admin_auth.logout()
        st.rerun()

    tab_nilai, tab_log, tab_notify, tab_audit = st.tabs(
        [t("admin_tab_kelola"), t("admin_tab_log"), t("admin_tab_notify"), t("admin_tab_audit")]
    )
    with tab_nilai:
        render_kelola_nilai(admin_user)
    with tab_log:
        render_log_akses()
    with tab_notify:
        render_notifikasi(admin_user)
    with tab_audit:
        render_audit_log()
