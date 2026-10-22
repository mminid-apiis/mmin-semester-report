import streamlit as st

LANGUAGES = {
    "id": "🇮🇩 Indonesia",
    "en": "🇬🇧 English",
    "zh": "🇨🇳 中文",
}

_TRANSLATIONS = {
    "id": {
        "app_title": "Laporan Semester MMin",
        "intro_caption": (
            "Masukkan email, kelas, dan nomor HP yang terdaftar saat pendaftaran "
            "program untuk melihat nilai dan kehadiran Anda."
        ),
        "lang_label": "🌐 Bahasa",
        "nav_student": "Laporan Semester",
        "nav_admin": "Admin",
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
        "incomplete_data_warning": (
            "Data belum lengkap untuk menentukan status kelulusan. Hubungi wali kelas Anda."
        ),
        "report_status_label": "STATUS KESELURUHAN",
        "report_status_pass": "MEMENUHI SYARAT",
        "report_status_fail": "BELUM MEMENUHI SYARAT",
        "report_weeks": "Berdasarkan {recorded} dari {total} minggu yang tercatat",
        "report_avg_kuis": "Rata-rata Kuis",
        "report_avg_kehadiran": "Rata-rata Kehadiran",
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
        "app_title": "MMin Semester Report",
        "intro_caption": (
            "Enter the email, class, and phone number you registered with to view "
            "your grades and attendance."
        ),
        "lang_label": "🌐 Language",
        "nav_student": "Semester Report",
        "nav_admin": "Admin",
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
        "incomplete_data_warning": (
            "Data is incomplete to determine pass status. Please contact your class advisor."
        ),
        "report_status_label": "OVERALL STATUS",
        "report_status_pass": "ELIGIBLE",
        "report_status_fail": "NOT YET ELIGIBLE",
        "report_weeks": "Based on {recorded} of {total} weeks recorded",
        "report_avg_kuis": "Quiz average",
        "report_avg_kehadiran": "Attendance average",
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
    "zh": {
        "app_title": "MMin 学期成绩单",
        "intro_caption": "请输入报名时登记的电子邮箱、班级和手机号码，以查看您的成绩和出勤情况。",
        "lang_label": "🌐 语言",
        "nav_student": "学期成绩单",
        "nav_admin": "管理员",
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
        "incomplete_data_warning": "数据不完整，无法判定及格状态，请联系班主任。",
        "report_status_label": "总体状态",
        "report_status_pass": "符合要求",
        "report_status_fail": "尚未符合要求",
        "report_weeks": "基于已记录的 {recorded}/{total} 周",
        "report_avg_kuis": "测验平均分",
        "report_avg_kehadiran": "出勤平均率",
        "catatan_subheader": "班主任备注",
        "err_not_configured": "应用程序配置有误，请联系管理员。",
        "err_network": "无法连接到成绩单服务器，请稍后再试。",
        "err_invalid_response": "服务器响应无效。",
        # --- Admin panel ---
        "admin_page_title": "管理面板",
        "admin_login_title": "以管理员身份登录",
        "admin_password_label": "管理员密码",
        "admin_login_button": "登录",
        "admin_account_label": "管理员账号",
        "admin_no_accounts": "尚未在 Secrets 中设置管理员账号（admin_accounts），请联系应用管理者。",
        "admin_wrong_credentials": "账号或密码错误。",
        "admin_locked": "失败次数过多，请在 {seconds} 秒后重试。",
        "admin_log_warning": "登录成功，但未能记录到管理员活动日志。请确认 Apps Script 已重新部署为最新版本。",
        "admin_signed_in_as": "已登录：**{user}**",
        "admin_logout_button": "退出登录",
        "admin_tab_kelola": "成绩管理",
        "admin_tab_log": "学生访问记录",
        "admin_tab_notify": "通知",
        "admin_tab_audit": "管理员活动日志",
        "admin_kelas_label": "选择班级",
        "admin_load_button": "从 Google 表格加载数据",
        "admin_loading_data": "正在加载数据...",
        "admin_load_error": "加载数据失败（{code}）。",
        "admin_load_error_generic": "加载数据失败。",
        "admin_load_hint": "点击「从 Google 表格加载数据」以开始管理该班级的成绩。",
        "admin_active_tab_caption": "当前表格：**{sheet}**",
        "admin_csv_upload_label": "或上传 CSV 文件一次性填充下方表格",
        "admin_csv_read_error": "读取 CSV 失败：{err}",
        "admin_csv_missing_cols": "CSV 缺少以下列，已留空：{cols}",
        "admin_csv_extra_cols": "以下 CSV 列已被忽略（表格中不存在）：{cols}",
        "admin_row_count_caption": "共 {n} 行学生数据。",
        "admin_confirm_save_label": "我确认要将这些更改保存到 Google 表格（将覆盖该表中的旧数据）。",
        "admin_save_button": "保存到 Google 表格",
        "admin_saving_spinner": "正在保存...",
        "admin_save_error": "保存失败（{code}）。",
        "admin_save_error_generic": "保存失败。",
        "admin_save_success": (
            "已将 {n} 行保存到 Google 表格（修改 {ubah} 个单元格，新增 {tambah} 位学生，删除 {hapus} 位学生）。"
        ),
        "admin_save_conflict": (
            "保存失败：自您加载以来，Google 表格中的数据已被更改（可能是其他管理员先保存了）。"
            "请重新加载数据，然后重新进行修改。"
        ),
        "admin_save_conflict_download": "下载我的表格（CSV）作为备份",
        "admin_load_log_button": "加载访问记录",
        "admin_loading_log": "正在加载访问记录...",
        "admin_log_load_error": "加载记录失败（{code}）。",
        "admin_log_load_error_generic": "加载记录失败。",
        "admin_log_hint": "点击「加载访问记录」以查看学生的访问历史。",
        "admin_log_empty": "目前还没有学生访问记录。",
        "admin_filter_kelas_label": "按班级筛选",
        "admin_filter_all": "所有班级",
        "admin_summary_subheader": "每位学生的汇总",
        "admin_col_jumlah_akses": "访问次数",
        "admin_col_terakhir_diakses": "最后访问时间",
        "admin_raw_log_expander": "查看所有访问记录（原始数据）",
        "admin_missing_subheader": "从未打开过成绩单的学生",
        "admin_check_now_button": "立即检查",
        "admin_comparing_spinner": "正在与学生名单比对...",
        "admin_missing_warning": "有 {n} 位学生从未打开过成绩单：",
        "admin_missing_none": "所有学生（表格中有数据的）都已打开过他们的成绩单。",
        # --- Admin: 活动日志 ---
        "admin_audit_load_button": "加载管理员活动日志",
        "admin_audit_loading": "正在加载活动日志...",
        "admin_audit_load_error": "加载活动日志失败（{code}）。",
        "admin_audit_load_error_generic": "加载活动日志失败。",
        "admin_audit_hint": "点击「加载管理员活动日志」以查看谁登录过、修改了什么。",
        "admin_audit_empty": "目前还没有管理员活动记录。",
        "admin_audit_login_subheader": "各管理员登录情况",
        "admin_col_admin": "管理员",
        "admin_col_jumlah_login": "登录次数",
        "admin_col_login_terakhir": "最后登录时间",
        "admin_col_login_gagal": "登录失败次数",
        "admin_audit_filter_admin": "按管理员筛选",
        "admin_audit_filter_all": "所有管理员",
        "admin_audit_filter_aksi": "按操作筛选",
        "admin_audit_all_subheader": "全部活动（最新在前）",
        "admin_action_login": "登录",
        "admin_action_login_gagal": "登录失败",
        "admin_action_logout": "退出登录",
        "admin_action_simpan_nilai": "保存成绩",
        "admin_action_ubah_nilai": "修改成绩",
        "admin_action_tambah_siswa": "新增学生",
        "admin_action_hapus_siswa": "删除学生",
        "admin_action_simpan_ditolak": "保存被拒绝（冲突）",
        "admin_action_kirim_notifikasi": "发送通知",
        "admin_action_kirim_tes": "发送示例邮件",
        # --- Admin: 邮件通知 ---
        "admin_notify_intro": (
            "向学生发送包含成绩单链接的邮件。邮件只包含链接和查看方法，"
            "不包含成绩、及格状态或及格要求。"
        ),
        "admin_notify_load_button": "加载通知状态",
        "admin_notify_loading": "正在加载状态...",
        "admin_notify_load_error": "加载通知状态失败（{code}）。",
        "admin_notify_load_error_generic": "加载通知状态失败。",
        "admin_notify_hint": "点击「加载通知状态」开始。",
        "admin_notify_active_tab_caption": "当前表格：**{sheet}** · 学期：**{semester}**",
        "admin_notify_metric_quota": "今日剩余邮件额度",
        "admin_notify_metric_students": "本班学生数",
        "admin_notify_metric_invalid": "邮箱为空/无效",
        "admin_notify_invalid_expander": "没有有效邮箱的学生（不会发送）",
        "admin_notify_jenis_label": "邮件类型",
        "admin_notify_jenis_baru": "新成绩单已发布",
        "admin_notify_jenis_pengingat": "提醒（尚未查看）",
        "admin_notify_force_label": "同时重新发送给已收到/刚被提醒过的学生",
        "admin_notify_plan_summary": "将发送给 **{n}** 位学生。",
        "admin_notify_nothing": "目前没有学生需要此类型的邮件。",
        "admin_notify_skipped_summary": "已跳过：{parts}。",
        "admin_notify_reason_sudah_dikirim": "已收到",
        "admin_notify_reason_sudah_membuka": "已查看本学期成绩单",
        "admin_notify_reason_baru_diingatkan": "刚被提醒过",
        "admin_notify_recipients_expander": "查看收件人名单",
        "admin_notify_skipped_expander": "查看被跳过的学生",
        "admin_col_alasan": "原因",
        "admin_col_jenis": "类型",
        "admin_col_status": "状态",
        "admin_notify_preview_expander": "查看将要发送的邮件内容",
        "admin_notify_preview_note": "学生姓名会自动替换为每位收件人的姓名。邮件中的链接指向本应用。",
        "admin_notify_preview_subject": "主题：{subject}",
        "admin_notify_test_button": "发送示例邮件到 {owner}",
        "admin_notify_test_spinner": "正在发送示例邮件...",
        "admin_notify_test_ok": "示例邮件已发送到 {to}（不会发给学生）。",
        "admin_notify_test_error": "发送示例邮件失败（{code}）。",
        "admin_notify_quota_exhausted": "今日邮件额度已用完，请明天再试。",
        "admin_notify_quota_low": (
            "剩余邮件额度（{quota}）少于收件人数（{n}）。额度用完时发送会停止，剩余部分可明天继续。"
        ),
        "admin_notify_confirm": "我已检查邮件内容，确认发送给 {kelas} 的 {n} 位学生。",
        "admin_notify_send_button": "发送给 {n} 位学生",
        "admin_notify_sending": "正在发送... {done}/{total}",
        "admin_notify_done": "完成：已发送 {sent} 封邮件。",
        "admin_notify_done_failed": "有 {n} 封邮件发送失败：{emails}",
        "admin_notify_send_error": "发送已中止（{code}）。",
        "admin_notify_send_error_generic": "发送已中止。",
        "admin_notify_history_subheader": "最近发送记录",
    },
}


def get_lang() -> str:
    return st.session_state.get("lang") or "id"


def t(key: str, **kwargs) -> str:
    text = _TRANSLATIONS.get(get_lang(), _TRANSLATIONS["id"]).get(key, key)
    return text.format(**kwargs) if kwargs else text


def render_language_switcher():
    """Tombol segmented ID/EN/ZH -- dipakai di halaman siswa maupun admin."""
    codes = list(LANGUAGES.keys())
    st.segmented_control(
        t("lang_label"),
        options=codes,
        format_func=lambda code: LANGUAGES[code],
        default=get_lang(),
        required=True,
        key="lang",
        label_visibility="collapsed",
    )
