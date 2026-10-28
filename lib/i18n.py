import streamlit as st

_TRANSLATIONS = {
    "id": {
        "app_title": "Laporan Semester",
        "app_title_accent": "MMin",
        "intro_caption": (
            "Masukkan email yang Anda daftarkan dan pilih kelas Anda untuk melihat "
            "rata-rata kuis dan kehadiran Anda."
        ),
        "lang_label": "🌐 Bahasa",
        "nav_student": "Laporan Semester",
        "nav_admin": "Admin",
        "no_semesters_error": "Laporan belum tersedia saat ini. Hubungi wali kelas Anda.",
        "email_label": "Email",
        "email_placeholder": "nama@email.com",
        "kelas_label": "Kelas",
        "kelas_placeholder": "Pilih kelas Anda",
        "submit_button": "Lihat laporan",
        "spinner_search": "Mencari data...",
        "warning_incomplete": "Lengkapi email dan kelas terlebih dahulu.",
        "error_not_found": (
            "Data tidak ditemukan. Pastikan email dan kelas sesuai dengan "
            "data pendaftaran Anda."
        ),
        "incomplete_data_warning": (
            "Data belum lengkap untuk menentukan status kelulusan. Hubungi wali kelas Anda."
        ),
        "report_status_label": "STATUS KESELURUHAN",
        "report_status_pass": "ANDA MEMENUHI SYARAT UNTUK MELANJUTKAN DI SEMESTER 3",
        "report_status_fail": "ANDA TIDAK MEMENUHI SYARAT UNTUK MELANJUTKAN DI SEMESTER 3",
        "report_status_warn": "LULUS BERSYARAT: DIHARAPKAN ADA PENINGKATAN SECARA SIGNIFIKAN DI SEMESTER 3.",
        "report_weeks": "Berdasarkan {recorded} dari {total} minggu yang tercatat",
        "report_avg_kuis": "Rata-rata Kuis",
        "report_avg_kehadiran": "Rata-rata Kehadiran",
        "report_note": "Catatan: nilai ini adalah nilai akumulasi dari Semester 1 dan 2.",
        "report_rank": "Peringkat Anda di kelas adalah {position} dari {total} siswa",
        "help_not_found": "Email tidak ditemukan? Silakan hubungi Admin MMin Indonesia.",
        "lookup_another_button": "Periksa Status Lain",
        "catatan_subheader": "Catatan wali kelas",
        "err_not_configured": "Aplikasi belum dikonfigurasi dengan benar. Hubungi admin.",
        "err_network": "Tidak bisa terhubung ke server laporan. Coba lagi beberapa saat lagi.",
        "err_invalid_response": "Respons server tidak valid.",
        # --- Admin panel ---
        "admin_page_title": "Admin Panel",
        "admin_login_title": "Masuk sebagai admin",
        "admin_password_label": "Password admin",
        "admin_login_button": "Masuk",
        "admin_account_label": "Akun admin",
        "admin_no_accounts": (
            "Akun admin belum diatur di Secrets (admin_accounts). Hubungi pengelola aplikasi."
        ),
        "admin_wrong_credentials": "Akun atau password salah.",
        "admin_locked": "Terlalu banyak percobaan gagal. Coba lagi dalam {seconds} detik.",
        "admin_log_warning": (
            "Login berhasil, tetapi gagal dicatat ke log aktivitas admin. "
            "Pastikan Apps Script sudah di-deploy ulang ke versi terbaru."
        ),
        "admin_signed_in_as": "Masuk sebagai **{user}**",
        "admin_logout_button": "Keluar",
        "admin_tab_kelola": "Kelola Nilai",
        "admin_tab_log": "Log Akses Siswa",
        "admin_tab_notify": "Notifikasi",
        "admin_tab_audit": "Log Aktivitas Admin",
        "admin_kelas_label": "Pilih kelas",
        "admin_load_button": "Muat data dari Google Sheets",
        "admin_loading_data": "Memuat data...",
        "admin_load_error": "Gagal memuat data ({code}).",
        "admin_load_error_generic": "Gagal memuat data.",
        "admin_load_hint": 'Klik "Muat data dari Google Sheets" untuk mulai mengelola nilai kelas ini.',
        "admin_active_tab_caption": "Tab aktif: **{sheet}**",
        "admin_csv_upload_label": "Atau unggah CSV untuk mengisi tabel di bawah sekaligus",
        "admin_csv_read_error": "Gagal membaca CSV: {err}",
        "admin_csv_missing_cols": "Kolom CSV tidak lengkap, dikosongkan: {cols}",
        "admin_csv_extra_cols": "Kolom CSV ini diabaikan (tidak ada di sheet): {cols}",
        "admin_row_count_caption": "{n} baris siswa.",
        "admin_confirm_save_label": (
            "Saya yakin ingin menyimpan perubahan ini ke Google Sheets "
            "(menimpa data lama di tab ini)."
        ),
        "admin_save_button": "Simpan ke Google Sheets",
        "admin_saving_spinner": "Menyimpan...",
        "admin_save_error": "Gagal menyimpan ({code}).",
        "admin_save_error_generic": "Gagal menyimpan.",
        "admin_save_success": (
            "Tersimpan {n} baris ke Google Sheets "
            "(ubah {ubah} sel, tambah {tambah} siswa, hapus {hapus} siswa)."
        ),
        "admin_save_conflict": (
            "Gagal menyimpan: data di Google Sheets sudah berubah sejak Anda memuatnya "
            "(kemungkinan admin lain sudah menyimpan lebih dulu). Muat ulang data, "
            "lalu ulangi perubahan Anda."
        ),
        "admin_save_conflict_download": "Unduh tabel saya (CSV) sebagai cadangan",
        "admin_load_log_button": "Muat log akses",
        "admin_loading_log": "Memuat log akses...",
        "admin_log_load_error": "Gagal memuat log ({code}).",
        "admin_log_load_error_generic": "Gagal memuat log.",
        "admin_log_hint": 'Klik "Muat log akses" untuk melihat riwayat akses siswa.',
        "admin_log_empty": "Belum ada catatan akses siswa.",
        "admin_filter_kelas_label": "Filter kelas",
        "admin_filter_all": "Semua kelas",
        "admin_summary_subheader": "Ringkasan per siswa",
        "admin_col_jumlah_akses": "Jumlah Akses",
        "admin_col_terakhir_diakses": "Terakhir Diakses",
        "admin_raw_log_expander": "Lihat semua catatan akses (mentah)",
        "admin_missing_subheader": "Siswa yang belum pernah membuka laporannya",
        "admin_check_now_button": "Cek sekarang",
        "admin_comparing_spinner": "Membandingkan dengan daftar siswa...",
        "admin_missing_warning": "{n} siswa belum pernah membuka laporan mereka:",
        "admin_missing_none": (
            "Semua siswa (yang datanya ada di sheet) pernah membuka laporan mereka."
        ),
        # --- Admin: log aktivitas ---
        "admin_audit_load_button": "Muat log aktivitas admin",
        "admin_audit_loading": "Memuat log aktivitas...",
        "admin_audit_load_error": "Gagal memuat log aktivitas ({code}).",
        "admin_audit_load_error_generic": "Gagal memuat log aktivitas.",
        "admin_audit_hint": (
            'Klik "Muat log aktivitas admin" untuk melihat siapa yang login dan mengubah apa.'
        ),
        "admin_audit_empty": "Belum ada aktivitas admin yang tercatat.",
        "admin_audit_login_subheader": "Login per admin",
        "admin_col_admin": "Admin",
        "admin_col_jumlah_login": "Jumlah Login",
        "admin_col_login_terakhir": "Login Terakhir",
        "admin_col_login_gagal": "Login Gagal",
        "admin_audit_filter_admin": "Filter admin",
        "admin_audit_filter_all": "Semua admin",
        "admin_audit_filter_aksi": "Filter aksi",
        "admin_audit_all_subheader": "Semua aktivitas (terbaru di atas)",
        "admin_action_login": "Login",
        "admin_action_login_gagal": "Login gagal",
        "admin_action_logout": "Logout",
        "admin_action_simpan_nilai": "Simpan nilai",
        "admin_action_ubah_nilai": "Ubah nilai",
        "admin_action_tambah_siswa": "Tambah siswa",
        "admin_action_hapus_siswa": "Hapus siswa",
        "admin_action_simpan_ditolak": "Simpan ditolak (konflik)",
        "admin_action_kirim_notifikasi": "Kirim notifikasi",
        "admin_action_kirim_tes": "Kirim email contoh",
        # --- Admin: notifikasi email ---
        "admin_notify_intro": (
            "Kirim email berisi link laporan ke siswa. Email hanya berisi link dan cara "
            "membukanya — tidak memuat nilai, status kelulusan, maupun syaratnya."
        ),
        "admin_notify_load_button": "Muat status notifikasi",
        "admin_notify_loading": "Memuat status...",
        "admin_notify_load_error": "Gagal memuat status notifikasi ({code}).",
        "admin_notify_load_error_generic": "Gagal memuat status notifikasi.",
        "admin_notify_hint": 'Klik "Muat status notifikasi" untuk mulai.',
        "admin_notify_active_tab_caption": "Tab aktif: **{sheet}** · semester: **{semester}**",
        "admin_notify_metric_quota": "Sisa kuota email hari ini",
        "admin_notify_metric_students": "Siswa di kelas ini",
        "admin_notify_metric_invalid": "Email kosong/tidak valid",
        "admin_notify_invalid_expander": "Siswa tanpa email valid (tidak akan dikirimi)",
        "admin_notify_jenis_label": "Jenis email",
        "admin_notify_jenis_baru": "Laporan baru tersedia",
        "admin_notify_jenis_pengingat": "Pengingat (belum membuka)",
        "admin_notify_force_label": (
            "Kirim ulang juga ke yang sudah menerima / baru diingatkan"
        ),
        "admin_notify_plan_summary": "Akan dikirim ke **{n}** siswa.",
        "admin_notify_nothing": "Tidak ada siswa yang perlu dikirimi untuk jenis email ini.",
        "admin_notify_skipped_summary": "Dilewati: {parts}.",
        "admin_notify_reason_sudah_dikirim": "sudah menerima",
        "admin_notify_reason_sudah_membuka": "sudah membuka laporan semester ini",
        "admin_notify_reason_baru_diingatkan": "baru diingatkan",
        "admin_notify_recipients_expander": "Lihat daftar penerima",
        "admin_notify_skipped_expander": "Lihat siapa yang dilewati",
        "admin_col_alasan": "Alasan",
        "admin_col_jenis": "Jenis",
        "admin_col_status": "Status",
        "admin_notify_preview_expander": "Lihat isi email yang akan dikirim",
        "admin_notify_preview_note": (
            "Nama siswa diganti otomatis untuk tiap penerima. "
            "Link di email mengarah ke aplikasi ini."
        ),
        "admin_notify_preview_subject": "Subjek: {subject}",
        "admin_notify_test_button": "Kirim email contoh ke {owner}",
        "admin_notify_test_spinner": "Mengirim email contoh...",
        "admin_notify_test_ok": "Email contoh terkirim ke {to} (bukan ke siswa).",
        "admin_notify_test_error": "Gagal mengirim email contoh ({code}).",
        "admin_notify_quota_exhausted": "Kuota email harian sudah habis. Coba lagi besok.",
        "admin_notify_quota_low": (
            "Sisa kuota email ({quota}) lebih sedikit dari jumlah penerima ({n}). "
            "Pengiriman akan berhenti saat kuota habis; sisanya bisa dilanjutkan besok."
        ),
        "admin_notify_confirm": (
            "Saya sudah memeriksa isi email dan yakin mengirim ke {n} siswa kelas {kelas}."
        ),
        "admin_notify_send_button": "Kirim ke {n} siswa",
        "admin_notify_sending": "Mengirim... {done}/{total}",
        "admin_notify_done": "Selesai: {sent} email terkirim.",
        "admin_notify_done_failed": "{n} email gagal terkirim: {emails}",
        "admin_notify_send_error": "Pengiriman terhenti ({code}).",
        "admin_notify_send_error_generic": "Pengiriman terhenti.",
        "admin_notify_history_subheader": "Riwayat pengiriman terakhir",
    },
    "en": {
        "app_title": "MMin Semester",
        "app_title_accent": "Report",
        "intro_caption": (
            "Enter the email you registered with and choose your class to view "
            "your quiz and attendance averages."
        ),
        "lang_label": "🌐 Language",
        "nav_student": "Semester Report",
        "nav_admin": "Admin",
        "no_semesters_error": "Reports are not available right now. Please contact your class advisor.",
        "email_label": "Email",
        "email_placeholder": "name@email.com",
        "kelas_label": "Class",
        "kelas_placeholder": "Select your class",
        "submit_button": "View report",
        "spinner_search": "Searching...",
        "warning_incomplete": "Please fill in email and class first.",
        "error_not_found": (
            "Data not found. Please make sure your email and class "
            "match your registration."
        ),
        "incomplete_data_warning": (
            "Data is incomplete to determine pass status. Please contact your class advisor."
        ),
        "report_status_label": "OVERALL STATUS",
        "report_status_pass": "YOU MEET THE REQUIREMENTS TO CONTINUE TO SEMESTER 3",
        "report_status_fail": "YOU DO NOT MEET THE REQUIREMENTS TO CONTINUE TO SEMESTER 3",
        "report_status_warn": "CONDITIONAL PASS: A SIGNIFICANT IMPROVEMENT IS EXPECTED IN SEMESTER 3.",
        "report_weeks": "Based on {recorded} of {total} weeks recorded",
        "report_avg_kuis": "Quiz average",
        "report_avg_kehadiran": "Attendance average",
        "report_note": "Note: these scores are cumulative scores from Semesters 1 and 2.",
        "report_rank": "Your rank in the class is {position} out of {total} students",
        "help_not_found": "Email not found? Please contact the MMin Indonesia Admin.",
        "lookup_another_button": "Check Another Status",
        "catatan_subheader": "Class advisor's note",
        "err_not_configured": "The app is not configured correctly. Please contact the admin.",
        "err_network": "Could not connect to the report server. Please try again shortly.",
        "err_invalid_response": "Invalid server response.",
        # --- Admin panel ---
        "admin_page_title": "Admin Panel",
        "admin_login_title": "Sign in as admin",
        "admin_password_label": "Admin password",
        "admin_login_button": "Sign in",
        "admin_account_label": "Admin account",
        "admin_no_accounts": (
            "Admin accounts are not set up in Secrets (admin_accounts). "
            "Please contact the app maintainer."
        ),
        "admin_wrong_credentials": "Incorrect account or password.",
        "admin_locked": "Too many failed attempts. Try again in {seconds} seconds.",
        "admin_log_warning": (
            "Signed in, but the login could not be recorded in the admin activity log. "
            "Make sure Apps Script has been redeployed with the latest version."
        ),
        "admin_signed_in_as": "Signed in as **{user}**",
        "admin_logout_button": "Log out",
        "admin_tab_kelola": "Manage Grades",
        "admin_tab_log": "Student Access Log",
        "admin_tab_notify": "Notifications",
        "admin_tab_audit": "Admin Activity Log",
        "admin_kelas_label": "Select class",
        "admin_load_button": "Load data from Google Sheets",
        "admin_loading_data": "Loading data...",
        "admin_load_error": "Failed to load data ({code}).",
        "admin_load_error_generic": "Failed to load data.",
        "admin_load_hint": 'Click "Load data from Google Sheets" to start managing this class\'s grades.',
        "admin_active_tab_caption": "Active tab: **{sheet}**",
        "admin_csv_upload_label": "Or upload a CSV to fill the table below at once",
        "admin_csv_read_error": "Failed to read CSV: {err}",
        "admin_csv_missing_cols": "CSV is missing these columns, left blank: {cols}",
        "admin_csv_extra_cols": "These CSV columns were ignored (not in the sheet): {cols}",
        "admin_row_count_caption": "{n} student rows.",
        "admin_confirm_save_label": (
            "I confirm I want to save these changes to Google Sheets "
            "(this overwrites the old data in this tab)."
        ),
        "admin_save_button": "Save to Google Sheets",
        "admin_saving_spinner": "Saving...",
        "admin_save_error": "Failed to save ({code}).",
        "admin_save_error_generic": "Failed to save.",
        "admin_save_success": (
            "Saved {n} rows to Google Sheets "
            "(changed {ubah} cells, added {tambah} students, removed {hapus} students)."
        ),
        "admin_save_conflict": (
            "Could not save: the data in Google Sheets changed after you loaded it "
            "(another admin probably saved first). Reload the data, then redo your changes."
        ),
        "admin_save_conflict_download": "Download my table (CSV) as a backup",
        "admin_load_log_button": "Load access log",
        "admin_loading_log": "Loading access log...",
        "admin_log_load_error": "Failed to load log ({code}).",
        "admin_log_load_error_generic": "Failed to load log.",
        "admin_log_hint": 'Click "Load access log" to view students\' access history.',
        "admin_log_empty": "No student access records yet.",
        "admin_filter_kelas_label": "Filter by class",
        "admin_filter_all": "All classes",
        "admin_summary_subheader": "Per-student summary",
        "admin_col_jumlah_akses": "Access Count",
        "admin_col_terakhir_diakses": "Last Accessed",
        "admin_raw_log_expander": "View all access records (raw)",
        "admin_missing_subheader": "Students who have never opened their report",
        "admin_check_now_button": "Check now",
        "admin_comparing_spinner": "Comparing with student roster...",
        "admin_missing_warning": "{n} students have never opened their report:",
        "admin_missing_none": (
            "All students (whose data is in the sheet) have opened their report."
        ),
        # --- Admin: activity log ---
        "admin_audit_load_button": "Load admin activity log",
        "admin_audit_loading": "Loading activity log...",
        "admin_audit_load_error": "Failed to load activity log ({code}).",
        "admin_audit_load_error_generic": "Failed to load activity log.",
        "admin_audit_hint": (
            'Click "Load admin activity log" to see who signed in and what they changed.'
        ),
        "admin_audit_empty": "No admin activity recorded yet.",
        "admin_audit_login_subheader": "Sign-ins per admin",
        "admin_col_admin": "Admin",
        "admin_col_jumlah_login": "Sign-in Count",
        "admin_col_login_terakhir": "Last Sign-in",
        "admin_col_login_gagal": "Failed Sign-ins",
        "admin_audit_filter_admin": "Filter by admin",
        "admin_audit_filter_all": "All admins",
        "admin_audit_filter_aksi": "Filter by action",
        "admin_audit_all_subheader": "All activity (newest first)",
        "admin_action_login": "Sign-in",
        "admin_action_login_gagal": "Failed sign-in",
        "admin_action_logout": "Sign-out",
        "admin_action_simpan_nilai": "Save grades",
        "admin_action_ubah_nilai": "Edit grade",
        "admin_action_tambah_siswa": "Add student",
        "admin_action_hapus_siswa": "Remove student",
        "admin_action_simpan_ditolak": "Save rejected (conflict)",
        "admin_action_kirim_notifikasi": "Send notification",
        "admin_action_kirim_tes": "Send sample email",
        # --- Admin: email notifications ---
        "admin_notify_intro": (
            "Send students an email with the link to their report. The email only contains "
            "the link and how to open it — no grades, pass status, or requirements."
        ),
        "admin_notify_load_button": "Load notification status",
        "admin_notify_loading": "Loading status...",
        "admin_notify_load_error": "Failed to load notification status ({code}).",
        "admin_notify_load_error_generic": "Failed to load notification status.",
        "admin_notify_hint": 'Click "Load notification status" to get started.',
        "admin_notify_active_tab_caption": "Active tab: **{sheet}** · semester: **{semester}**",
        "admin_notify_metric_quota": "Email quota left today",
        "admin_notify_metric_students": "Students in this class",
        "admin_notify_metric_invalid": "Missing/invalid email",
        "admin_notify_invalid_expander": "Students without a valid email (will not be emailed)",
        "admin_notify_jenis_label": "Email type",
        "admin_notify_jenis_baru": "New report available",
        "admin_notify_jenis_pengingat": "Reminder (not opened yet)",
        "admin_notify_force_label": "Also resend to those who already received / were just reminded",
        "admin_notify_plan_summary": "Will be sent to **{n}** students.",
        "admin_notify_nothing": "No students need this email type right now.",
        "admin_notify_skipped_summary": "Skipped: {parts}.",
        "admin_notify_reason_sudah_dikirim": "already received",
        "admin_notify_reason_sudah_membuka": "already opened this semester's report",
        "admin_notify_reason_baru_diingatkan": "recently reminded",
        "admin_notify_recipients_expander": "View recipient list",
        "admin_notify_skipped_expander": "View who is skipped",
        "admin_col_alasan": "Reason",
        "admin_col_jenis": "Type",
        "admin_col_status": "Status",
        "admin_notify_preview_expander": "View the email that will be sent",
        "admin_notify_preview_note": (
            "The student's name is filled in automatically for each recipient. "
            "The link in the email points to this app."
        ),
        "admin_notify_preview_subject": "Subject: {subject}",
        "admin_notify_test_button": "Send a sample email to {owner}",
        "admin_notify_test_spinner": "Sending sample email...",
        "admin_notify_test_ok": "Sample email sent to {to} (not to students).",
        "admin_notify_test_error": "Failed to send sample email ({code}).",
        "admin_notify_quota_exhausted": "Today's email quota is used up. Try again tomorrow.",
        "admin_notify_quota_low": (
            "Remaining email quota ({quota}) is lower than the number of recipients ({n}). "
            "Sending will stop when the quota runs out; the rest can continue tomorrow."
        ),
        "admin_notify_confirm": (
            "I have checked the email and I'm sure I want to send it to {n} students in {kelas}."
        ),
        "admin_notify_send_button": "Send to {n} students",
        "admin_notify_sending": "Sending... {done}/{total}",
        "admin_notify_done": "Done: {sent} emails sent.",
        "admin_notify_done_failed": "{n} emails failed to send: {emails}",
        "admin_notify_send_error": "Sending stopped ({code}).",
        "admin_notify_send_error_generic": "Sending stopped.",
        "admin_notify_history_subheader": "Recent sending history",
    },
}


def get_lang() -> str:
    lang = st.session_state.get("lang")
    return lang if lang in _TRANSLATIONS else "id"


def t(key: str, **kwargs) -> str:
    text = _TRANSLATIONS.get(get_lang(), _TRANSLATIONS["id"]).get(key, key)
    return text.format(**kwargs) if kwargs else text


def _on_lang_toggle():
    st.session_state["lang"] = "id" if st.session_state["lang_toggle"] else "en"


def render_language_switcher():
    """Satu tombol geser EN | ID di pojok kanan atas (tata letak & bendera ada di
    lib/branding.py, kelas `.st-key-langswitch`). Posisi kiri = English (mati),
    kanan = Indonesia (hidup). Dipanggil sekali dari app.py untuk semua halaman."""
    st.session_state["lang_toggle"] = get_lang() == "id"
    with st.container(key="langswitch"):
        st.toggle(
            t("lang_label"),
            key="lang_toggle",
            on_change=_on_lang_toggle,
            label_visibility="collapsed",
        )
