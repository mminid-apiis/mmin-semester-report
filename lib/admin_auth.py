"""Login admin multi-akun (admin1..admin4, dst.) + pencatatan ke log aktivitas admin.

Akun didefinisikan di tabel `[admin_accounts]` pada secrets (satu key = satu
akun, nilainya password). Setiap sesi browser punya login sendiri, jadi
beberapa admin bisa masuk bersamaan; setiap login, login gagal, dan logout
dicatat ke Google Sheets lewat Apps Script (tab `_AdminAuditLog`).
"""

from __future__ import annotations

import hmac
import time

import streamlit as st

from lib.apps_script_client import AppsScriptError, call_apps_script

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300

LOGIN_OK = "ok"
LOGIN_OK_LOG_FAILED = "ok_log_failed"
LOGIN_WRONG = "wrong"
LOGIN_LOCKED = "locked"


def get_accounts() -> dict[str, str]:
    try:
        raw = st.secrets["admin_accounts"]
    except (KeyError, FileNotFoundError):
        return {}
    return {str(name): str(pw) for name, pw in raw.items() if str(pw)}


def current_admin() -> str | None:
    """Nama akun yang sedang login di sesi ini, atau None.

    Akun yang sudah dihapus dari secrets otomatis tidak dianggap login lagi.
    """
    user = st.session_state.get("admin_user")
    if user and user in get_accounts():
        return user
    return None


def seconds_locked() -> int:
    until = st.session_state.get("admin_locked_until", 0.0)
    return max(0, int(until - time.time() + 0.999))


def log_event(admin: str, event: str, detail: str = "") -> bool:
    """Catat event ke log aktivitas admin. False kalau gagal (tidak melempar error)."""
    try:
        result = call_apps_script("admin_log_event", {"admin": admin, "event": event, "detail": detail})
    except AppsScriptError:
        return False
    return bool(result.get("ok"))


def attempt_login(username: str, password: str) -> str:
    if seconds_locked() > 0:
        return LOGIN_LOCKED

    expected = get_accounts().get(username, "")
    password_ok = hmac.compare_digest(password.encode("utf-8"), expected.encode("utf-8"))

    if not (expected and password_ok):
        failures = st.session_state.get("admin_failed_attempts", 0) + 1
        st.session_state["admin_failed_attempts"] = failures
        if failures >= MAX_FAILED_ATTEMPTS:
            st.session_state["admin_locked_until"] = time.time() + LOCKOUT_SECONDS
            st.session_state["admin_failed_attempts"] = 0
        log_event(username, "login_gagal", "password salah")
        return LOGIN_WRONG

    st.session_state["admin_failed_attempts"] = 0
    st.session_state["admin_user"] = username
    return LOGIN_OK if log_event(username, "login") else LOGIN_OK_LOG_FAILED


def logout() -> None:
    user = st.session_state.get("admin_user")
    if user:
        log_event(user, "logout")
    for key in (
        "admin_user",
        "admin_df",
        "admin_df_kelas",
        "admin_sheet_name",
        "admin_version",
        "admin_log_rows",
        "admin_audit_rows",
        "admin_notify_status",
    ):
        st.session_state.pop(key, None)
