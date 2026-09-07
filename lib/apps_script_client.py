"""Klien HTTP tipis untuk backend Google Apps Script.

Semua pencarian & pencocokan data dilakukan di sisi Apps Script; modul ini
hanya mengirim request dan menerjemahkan error jaringan/format menjadi kode
error generik yang aman ditampilkan ke siswa (diterjemahkan oleh lib/i18n.py).
"""

from __future__ import annotations

import requests
import streamlit as st


class AppsScriptError(Exception):
    """Error dengan `code` generik (bukan teks) supaya bisa diterjemahkan di app.py."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _get_config() -> tuple[str, str]:
    try:
        url = st.secrets["apps_script_url"]
        secret = st.secrets["apps_script_secret"]
    except (KeyError, FileNotFoundError) as exc:
        print(f"[apps_script_client] secrets belum lengkap: {exc}")
        raise AppsScriptError("err_not_configured") from exc

    if not url or "GANTI" in url:
        raise AppsScriptError("err_not_configured")

    return url, secret


def call_apps_script(action: str, payload: dict | None = None, timeout: int = 20) -> dict:
    """Panggil satu `action` di Web App Apps Script dan kembalikan JSON-nya.

    Selalu mengembalikan dict berisi minimal key "ok". Kegagalan
    jaringan/parsing dilempar sebagai AppsScriptError(code); detail teknisnya
    di-print supaya bisa dicek lewat Streamlit Cloud logs.
    """
    url, secret = _get_config()
    body = {"action": action, "secret": secret}
    if payload:
        body.update(payload)

    try:
        response = requests.post(url, json=body, timeout=timeout)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as exc:
        print(f"[apps_script_client] request error action={action}: {exc}")
        raise AppsScriptError("err_network") from exc
    except ValueError as exc:
        snippet = response.text[:300] if "response" in locals() else ""
        print(f"[apps_script_client] JSON tidak valid action={action}: {snippet}")
        raise AppsScriptError("err_invalid_response") from exc

    if not isinstance(result, dict):
        print(f"[apps_script_client] respons bukan objek JSON action={action}: {result!r}")
        raise AppsScriptError("err_invalid_response")

    if not result.get("ok"):
        print(f"[apps_script_client] action={action} ok=false: {result.get('message')}")

    return result
