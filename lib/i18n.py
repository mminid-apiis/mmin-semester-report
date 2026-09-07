import streamlit as st

LANGUAGES = {
    "id": "Indonesia",
    "en": "English",
    "zh": "中文",
}

_TRANSLATIONS = {
    "id": {
        "app_title": "Laporan semester MMin",
        "intro_caption": (
            "Masukkan email, kelas, dan nomor HP yang terdaftar saat pendaftaran "
            "program untuk melihat nilai dan kehadiran Anda."
        ),
        "criteria_caption": (
            "Syarat kelulusan semester: kehadiran Kelas Zoom minimal {kehadiran_min}% "
            "dan total nilai kuis minimal {kuis_min}%."
        ),
        "lang_label": "🌐 Bahasa",
        "theme_label": "Tampilan",
        "theme_light": "☀️ Terang",
        "theme_dark": "🌙 Gelap",
        "no_semesters_error": "Laporan belum tersedia saat ini. Hubungi wali kelas Anda.",
        "email_label": "Email",
        "email_placeholder": "nama@email.com",
        "kelas_label": "Kelas",
        "kelas_placeholder": "Pilih kelas Anda",
        "phone_label": "Nomor HP",
        "phone_placeholder": "08xxxxxxxxxx",
        "submit_button": "Lihat laporan",
        "spinner_search": "Mencari data...",
        "warning_incomplete": "Lengkapi email, kelas, dan nomor HP terlebih dahulu.",
        "error_not_found": (
            "Data tidak ditemukan. Pastikan email, kelas, dan nomor HP sesuai dengan "
            "data pendaftaran Anda."
        ),
        "success_found": "Ditemukan laporan untuk **{nama}** — {kelas}, {semester}",
        "metric_kuis": "Total persentase kuis",
        "metric_kehadiran": "Total persentase kehadiran",
        "status_subheader": "Status kelulusan semester",
        "incomplete_data_warning": (
            "Data belum lengkap untuk menentukan status kelulusan. Hubungi wali kelas Anda."
        ),
        "line_kehadiran_ok": "Kehadiran Zoom: {v:.0f}% (memenuhi syarat)",
        "line_kehadiran_fail": "Kehadiran Zoom: {v:.0f}% (syarat minimal {min}%)",
        "line_kuis_ok": "Total kuis: {v:.0f}% (memenuhi syarat)",
        "line_kuis_fail": "Total kuis: {v:.0f}% (syarat minimal {min}%)",
        "status_pass": "Memenuhi syarat kelulusan {semester}",
        "status_fail": "Belum memenuhi syarat kelulusan {semester}",
        "catatan_subheader": "Catatan wali kelas",
        "err_not_configured": "Aplikasi belum dikonfigurasi dengan benar. Hubungi admin.",
        "err_network": "Tidak bisa terhubung ke server laporan. Coba lagi beberapa saat lagi.",
        "err_invalid_response": "Respons server tidak valid.",
    },
    "en": {
        "app_title": "MMin Semester Report",
        "intro_caption": (
            "Enter the email, class, and phone number you registered with to view "
            "your grades and attendance."
        ),
        "criteria_caption": (
            "Semester pass requirement: at least {kehadiran_min}% Zoom class "
            "attendance and at least {kuis_min}% total quiz score."
        ),
        "lang_label": "🌐 Language",
        "theme_label": "Appearance",
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        "no_semesters_error": "Reports are not available right now. Please contact your class advisor.",
        "email_label": "Email",
        "email_placeholder": "name@email.com",
        "kelas_label": "Class",
        "kelas_placeholder": "Select your class",
        "phone_label": "Phone number",
        "phone_placeholder": "08xxxxxxxxxx",
        "submit_button": "View report",
        "spinner_search": "Searching...",
        "warning_incomplete": "Please fill in email, class, and phone number first.",
        "error_not_found": (
            "Data not found. Please make sure your email, class, and phone number "
            "match your registration."
        ),
        "success_found": "Report found for **{nama}** — {kelas}, {semester}",
        "metric_kuis": "Total quiz percentage",
        "metric_kehadiran": "Total attendance percentage",
        "status_subheader": "Semester pass status",
        "incomplete_data_warning": (
            "Data is incomplete to determine pass status. Please contact your class advisor."
        ),
        "line_kehadiran_ok": "Zoom attendance: {v:.0f}% (meets requirement)",
        "line_kehadiran_fail": "Zoom attendance: {v:.0f}% (minimum required {min}%)",
        "line_kuis_ok": "Total quiz: {v:.0f}% (meets requirement)",
        "line_kuis_fail": "Total quiz: {v:.0f}% (minimum required {min}%)",
        "status_pass": "Meets the pass requirement for {semester}",
        "status_fail": "Does not yet meet the pass requirement for {semester}",
        "catatan_subheader": "Class advisor's note",
        "err_not_configured": "The app is not configured correctly. Please contact the admin.",
        "err_network": "Could not connect to the report server. Please try again shortly.",
        "err_invalid_response": "Invalid server response.",
    },
    "zh": {
        "app_title": "MMin 学期成绩单",
        "intro_caption": "请输入报名时登记的电子邮箱、班级和手机号码，以查看您的成绩和出勤情况。",
        "criteria_caption": (
            "本学期及格要求：Zoom 课堂出勤率至少 {kehadiran_min}%，"
            "测验总分至少 {kuis_min}%。"
        ),
        "lang_label": "🌐 语言",
        "theme_label": "外观",
        "theme_light": "☀️ 浅色",
        "theme_dark": "🌙 深色",
        "no_semesters_error": "目前暂无成绩单，请联系班主任。",
        "email_label": "电子邮箱",
        "email_placeholder": "name@email.com",
        "kelas_label": "班级",
        "kelas_placeholder": "请选择您的班级",
        "phone_label": "手机号码",
        "phone_placeholder": "08xxxxxxxxxx",
        "submit_button": "查看成绩单",
        "spinner_search": "正在查询...",
        "warning_incomplete": "请先填写电子邮箱、班级和手机号码。",
        "error_not_found": "未找到数据，请确认您的电子邮箱、班级和手机号码与报名信息一致。",
        "success_found": "已找到 **{nama}** 的成绩单 — {kelas}，{semester}",
        "metric_kuis": "测验总分百分比",
        "metric_kehadiran": "出勤总百分比",
        "status_subheader": "学期及格状态",
        "incomplete_data_warning": "数据不完整，无法判定及格状态，请联系班主任。",
        "line_kehadiran_ok": "Zoom 出勤率：{v:.0f}%（符合要求）",
        "line_kehadiran_fail": "Zoom 出勤率：{v:.0f}%（最低要求 {min}%）",
        "line_kuis_ok": "测验总分：{v:.0f}%（符合要求）",
        "line_kuis_fail": "测验总分：{v:.0f}%（最低要求 {min}%）",
        "status_pass": "已达到 {semester} 的及格要求",
        "status_fail": "尚未达到 {semester} 的及格要求",
        "catatan_subheader": "班主任备注",
        "err_not_configured": "应用程序配置有误，请联系管理员。",
        "err_network": "无法连接到成绩单服务器，请稍后再试。",
        "err_invalid_response": "服务器响应无效。",
    },
}


def get_lang() -> str:
    return st.session_state.get("lang", "id")


def t(key: str, **kwargs) -> str:
    text = _TRANSLATIONS.get(get_lang(), _TRANSLATIONS["id"]).get(key, key)
    return text.format(**kwargs) if kwargs else text
