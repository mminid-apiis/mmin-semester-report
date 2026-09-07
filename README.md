# MMin Semester Report

Portal Streamlit bagi siswa MMin (±240 orang, 2 kelas) untuk melihat laporan nilai
dan kehadiran semester mereka sendiri — menggantikan pengiriman nilai manual satu
per satu lewat Gmail.

Backend dibuat dengan **Google Apps Script** (bukan Google Cloud Console/OAuth) —
gratis penuh, **tidak perlu kartu kredit**. Semua data nilai & kehadiran disimpan
langsung di **Google Sheets** (satu tab per semester). Aplikasi ini sendiri tidak
punya database lokal maupun upload file, jadi aman dijalankan di Streamlit
Community Cloud.

## Cara kerja & privasi

1. Siswa memilih **Kelas** ("MMin 2 Leadership" / "MMin 2 Pastoral") dan mengetik
   **Nomor HP** yang sama seperti saat pendaftaran.
2. Streamlit mengirim kelas + nomor HP ke Apps Script (lewat POST + `SHARED_SECRET`).
3. Apps Script mencari baris yang cocok **persis** pada kombinasi Kelas + Nomor HP
   (nomor HP dinormalisasi ke format `08xxxxxxxxxx` dulu di kedua sisi), lalu
   **hanya mengembalikan satu baris itu**. Seluruh isi spreadsheet tidak pernah
   dikirim ke frontend.
4. Kalau tidak cocok, pesannya generik ("Data tidak ditemukan") — tidak
   diberitahu apakah kelas atau nomor HP yang salah, supaya tidak membantu orang
   menebak-nebak data siswa lain.

Anda (guru) mengisi/update nilai **langsung di Google Sheets** seperti biasa
(copy-paste/import CSV) — tidak ada form input di aplikasi ini.

## Struktur data di Google Sheets

- Satu **tab per semester**, misalnya `Semester 2 2026`. Nama tab inilah yang
  muncul sebagai pilihan "Semester" di aplikasi (tab yang namanya diawali `_`
  disembunyikan dari daftar — berguna untuk tab catatan/kerja internal Anda).
- Baris pertama = header. Wajib ada kolom **Kelas** dan **Nomor HP** (nama kolom
  tidak case-sensitive). Kolom lain bebas sesuai kebutuhan:
  - Kolom **Nama** ditampilkan sebagai judul laporan.
  - Kolom yang namanya mengandung kata "kehadiran"/"hadir"/"presensi" (mis.
    `Kehadiran (%)`) ditampilkan sebagai metrik kehadiran.
  - Kolom yang namanya mengandung kata "catatan" (mis. `Catatan Wali Kelas`)
    ditampilkan sebagai catatan wali kelas.
  - Kolom lainnya (mis. `Alkitab`, `Homiletika`, `Kepemimpinan`) otomatis
    ditampilkan sebagai tabel nilai per mata pelajaran — tidak perlu ubah kode
    kalau mata pelajaran berganti tiap semester, cukup ubah nama kolom di sheet.
- Contoh 5 baris dummy untuk uji coba: [`data/dummy_semester_2_2026.csv`](data/dummy_semester_2_2026.csv).

**Penting soal Nomor HP:** sebelum paste data, format kolom Nomor HP sebagai
**Plain text** (klik kolom → Format → Number → Plain text) agar angka 0 di depan
tidak hilang. Sebagai jaga-jaga, Apps Script di project ini tetap mendeteksi dan
memperbaiki nomor yang angka 0 di depannya sudah terlanjur hilang — tapi
memformat sebagai Plain text dari awal tetap cara paling aman untuk 240 data.

## Setup — Google Sheets & Apps Script (gratis, tanpa kartu kredit)

Ini **bukan** Google Cloud Console — tidak ada verifikasi kartu, tidak ada
tagihan. Cukup akun Google biasa.

### 1. Buat Spreadsheet

1. Buat Google Spreadsheet baru, ganti nama sesuai keinginan (mis. "MMin
   Semester Report — Data").
2. Buat tab pertama dengan nama **`Semester 2 2026`**, lalu isi baris pertama
   dengan header dari [`data/dummy_semester_2_2026.csv`](data/dummy_semester_2_2026.csv)
   dan paste 5 baris dummy-nya untuk uji coba (ingat: format kolom Nomor HP
   sebagai Plain text dulu sebelum paste).
3. Salin **ID spreadsheet** dari URL:
   `https://docs.google.com/spreadsheets/d/`**`ID_SPREADSHEET_INI`**`/edit` —
   hanya bagian ID-nya, bukan URL lengkap.

### 2. Buat Apps Script

1. Buka [script.google.com](https://script.google.com/), login dengan akun
   Google yang sama seperti pemilik spreadsheet di atas.
2. Klik **New project**.
3. Hapus kode default, lalu salin-tempel seluruh isi
   [`google_apps_script/Code.gs`](google_apps_script/Code.gs) dari project ini.
4. Isi dua konstanta di bagian atas kode:
   - `SPREADSHEET_ID` → ID spreadsheet dari langkah 1 (hanya ID-nya!).
   - `SHARED_SECRET` → salin nilai `apps_script_secret` dari
     `.streamlit/secrets.toml` (sudah digenerate otomatis di project ini) supaya
     kedua sisi cocok persis.
5. Beri nama project (misal "MMin Semester Report Backend"), simpan (Ctrl+S).

### 3. Deploy sebagai Web App

1. Klik **Deploy → New deployment**.
2. Klik ikon gerigi di samping "Select type" → pilih **Web app**.
3. Isi:
   - **Execute as**: `Me`.
   - **Who has access**: `Anyone` — **bukan** "Only myself", kalau salah pilih
     semua request dari Streamlit akan ditolak dengan error 401.
4. Klik **Deploy** → klik **Authorize access** → pilih akun Google Anda. Kalau
   muncul peringatan "Google hasn't verified this app", klik
   **Advanced/Lanjutan → Buka [nama project] (unsafe)** — aman karena Anda
   sendiri pembuat script-nya.
5. Salin **Web app URL** yang muncul (formatnya
   `https://script.google.com/macros/s/xxxxx/exec`).

**Catatan:** setiap kali Anda mengubah `Code.gs` di script.google.com, Anda wajib
membuat deployment baru agar perubahan aktif — URL Web App-nya tetap sama:

> Deploy → Manage deployments → Edit (ikon pensil) → Version: **New version** → Deploy

### 4. Hubungkan ke aplikasi

Isi `.streamlit/secrets.toml` (sudah ada, tinggal lengkapi 2 baris ini):

```toml
apps_script_url = "https://script.google.com/macros/s/xxxxx/exec"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/ID_SPREADSHEET_INI/edit"
```

(`apps_script_secret` sudah terisi otomatis dan harus sama dengan
`SHARED_SECRET` di `Code.gs` pada langkah 2.)

## Menjalankan secara lokal

```bash
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Uji coba dengan 5 data dummy

1. Pastikan tab `Semester 2 2026` sudah berisi 5 baris dari
   [`data/dummy_semester_2_2026.csv`](data/dummy_semester_2_2026.csv).
2. Jalankan `streamlit run app.py`, pilih semester "Semester 2 2026".
3. Coba kombinasi berikut untuk memverifikasi alur:
   - Kelas `MMin 2 Leadership` + HP `081234500001` → harus muncul laporan
     "Test Satu".
   - Kelas `MMin 2 Leadership` + HP `08123 4500 002` (dengan spasi) → harus tetap
     cocok dengan "Test Dua" (menguji normalisasi spasi).
   - Kelas `MMin 2 Leadership` + HP `+62 812-3450-0005` → harus cocok dengan
     "Test Lima" (data di sheet sengaja disimpan dalam format `+62`, menguji
     normalisasi dari kedua sisi).
   - Kelas `MMin 2 Pastoral` + HP `081234500001` (kelas salah) → harus muncul
     pesan generik "Data tidak ditemukan", bukan pesan spesifik.
4. Setelah semua kombinasi di atas berhasil, ganti isi tab dengan data 240 siswa
   yang sebenarnya (bisa buat tab baru untuk semester berikutnya, tab lama tetap
   ada sebagai arsip).

## Menambah semester baru

Cukup buat tab baru di spreadsheet yang sama dengan nama bebas (mis.
`Semester 1 2027`), isi header + data seperti biasa. Tab baru otomatis muncul
sebagai pilihan semester di aplikasi (bisa butuh sampai 5 menit karena daftar
semester di-cache) — tidak perlu ubah kode maupun deploy ulang Apps Script.

## Deploy ke Streamlit Community Cloud (gratis, tanpa kartu kredit)

1. Push kode project ini (**kecuali** `.streamlit/secrets.toml` — sudah masuk
   `.gitignore`, jangan pernah di-commit) ke sebuah repository GitHub.
   - Repo **harus public** — kalau private, OAuth Streamlit App sering gagal
     dengan error "this repository does not exist" karena hanya dapat izin ke
     repo publik secara default. Sebelum push, cek dulu betul-betul tidak ada
     `secrets.toml` yang ikut ter-commit (`git status`) — isinya sensitif.
2. Buka [share.streamlit.io](https://share.streamlit.io), login dengan akun
   GitHub.
3. Klik **New app**, pilih repo ini dan file utama `app.py`.
4. Di **Advanced settings → Secrets**, tempel isi `.streamlit/secrets.toml` Anda.
5. Klik **Deploy** — dapat URL publik seperti `https://nama-app.streamlit.app`
   yang bisa dibagikan ke siswa.

Karena semua data ada di Google Sheets (bukan file lokal), aplikasi ini aman
dijalankan di Streamlit Community Cloud — tidak ada risiko kehilangan data
walau container-nya di-restart.

## Troubleshooting

- **Error 401 / "Unauthorized"** dari Apps Script → cek `Who has access` di
  deployment harus `Anyone`, dan `apps_script_secret` di secrets.toml harus
  sama persis dengan `SHARED_SECRET` di `Code.gs` (setelah deploy versi baru).
- **"Laporan belum tersedia saat ini"** di halaman siswa → berarti
  `list_semesters` gagal atau spreadsheet tidak punya tab yang bisa dibaca; cek
  `SPREADSHEET_ID` di `Code.gs` (harus ID saja, bukan URL) dan pastikan akun
  yang deploy Apps Script punya akses ke spreadsheet tersebut.
- Detail error teknis sengaja tidak ditampilkan ke siswa (hanya pesan umum).
  Untuk debug, cek log lewat:
  - Streamlit Cloud: **Manage app → Cloud Logs** (pesan dari `print(...)` di
    `lib/apps_script_client.py`).
  - Apps Script: **Executions** (log dari `console.error(...)` di `Code.gs`).
