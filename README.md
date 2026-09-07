# MMin Semester Report

Portal Streamlit bagi siswa MMin (±240 orang, 2 kelas) untuk melihat laporan nilai
dan kehadiran semester mereka sendiri — menggantikan pengiriman nilai manual satu
per satu lewat Gmail.

Backend dibuat dengan **Google Apps Script** (bukan Google Cloud Console/OAuth) —
gratis penuh, **tidak perlu kartu kredit**. Semua data nilai & kehadiran disimpan
langsung di **Google Sheets** (satu tab per kelas per periode, mis. "Semester 2
Leadership" dan "Semester 2 Pastoral"). Aplikasi ini sendiri tidak punya
database lokal maupun upload file, jadi aman dijalankan di Streamlit Community
Cloud.

## Bahasa & tampilan

Siswa bisa mengganti **bahasa** (Indonesia / English / 中文) lewat kontrol di
atas halaman — pilihan ini tersimpan selama sesi browser mereka. Semua teks
antarmuka (label, pesan error, status kelulusan) ikut berubah bahasa; untuk
menambah/mengubah teks lihat [`lib/i18n.py`](lib/i18n.py) (satu dict per
bahasa, key harus sama persis di ketiganya). Kolom **Catatan** yang Anda isi
sendiri di Google Sheets **tidak** ikut diterjemahkan otomatis — akan tampil
apa adanya dalam bahasa yang Anda ketik.

Tampilannya sendiri **tetap** (tidak ada toggle terang/gelap) — gradasi navy
gelap dengan kartu putih membulat di tengah, terinspirasi halaman login APIIS
Volunteer App. Logo APIIS ([`assets/logo_apiis.png`](assets/logo_apiis.png))
dan motto "21st Century Training. For Christians. For Free" tampil di atas
kartu (motto sengaja tidak diterjemahkan — ini teks resmi organisasi, sama di
ketiga bahasa) dan juga dipakai sebagai favicon tab browser. Untuk ganti logo,
timpa file itu dengan nama yang sama, atau ubah path-nya di `app.py`
(`st.image(...)` di dalam `st.container(key="hero")` dan `page_icon=...` di
`st.set_page_config`). Warna, radius, dan font diatur di
[`.streamlit/config.toml`](.streamlit/config.toml) (`primaryColor`,
`borderColor`, `baseRadius`, `font`); gradasi latar, dua lingkaran cahaya di
pojok, dan kartu putihnya ada di [`lib/branding.py`](lib/branding.py). Kalau
Anda ubah `lib/branding.py` saat menjalankan lokal dan perubahannya tidak
muncul setelah refresh, **restart** `streamlit run` (bukan cuma reload
browser) — Python meng-cache modul yang
sudah di-import.

## Cara kerja & privasi

1. Siswa mengisi **Email**, memilih **Kelas** ("MMin 2 Leadership" / "MMin 2
   Pastoral"), dan mengetik **Nomor HP** — ketiganya harus sama seperti saat
   pendaftaran. Semester tidak dipilih siswa.
2. Streamlit mengirim email + kelas + nomor HP ke Apps Script (lewat POST +
   `SHARED_SECRET`).
3. Apps Script **memilih tab berdasarkan Kelas yang dipilih** (lihat "Struktur
   data" di bawah), lalu mencari baris di tab itu yang cocok **persis** pada
   kombinasi Email + Nomor HP (email dibandingkan tanpa memandang huruf
   besar/kecil, nomor HP dinormalisasi ke format `08xxxxxxxxxx` dulu di kedua
   sisi). Hanya **satu baris itu** yang dikembalikan — seluruh isi spreadsheet
   tidak pernah dikirim ke frontend.
4. Kalau salah satu saja tidak cocok (termasuk kalau siswa asal pilih Kelas
   yang salah, sehingga Apps Script membuka tab yang salah), pesannya generik
   ("Data tidak ditemukan") — tidak diberitahu bagian mana yang salah, supaya
   tidak membantu orang menebak-nebak data siswa lain.

Anda (guru) mengisi/update nilai **langsung di Google Sheets** seperti biasa
(copy-paste/import CSV) — tidak ada form input di aplikasi ini.

## Struktur data di Google Sheets

- **Satu tab per kelas per periode** — bukan satu tab untuk kedua kelas. Nama
  tab bebas, asalkan **kata terakhirnya sama dengan kata terakhir pada nilai
  Kelas**:
  - Kelas `MMin 2 Leadership` → nama tab harus mengandung kata **Leadership**
    di akhir, mis. `Semester 2 Leadership`.
  - Kelas `MMin 2 Pastoral` → nama tab harus mengandung kata **Pastoral** di
    akhir, mis. `Semester 2 Pastoral`.

  Apps Script mencari tab berdasarkan Kelas yang dipilih siswa (pencocokan kata
  kunci ini tidak case-sensitive). Tab yang namanya diawali `_` disembunyikan/
  diabaikan (berguna untuk tab catatan/kerja internal Anda).

- **Semester tidak dipilih siswa** — kalau ada beberapa tab yang cocok untuk
  kelas yang sama (semester lama masih disimpan sebagai arsip, lihat "Menambah
  semester baru" di bawah), yang otomatis dipakai adalah tab **paling kanan**
  di antara tab-tab untuk kelas itu.

- Baris pertama tiap tab = header, kolomnya tetap (nama kolom tidak
  case-sensitive):

  | Kolom | Keterangan |
  |---|---|
  | `Email` | dipakai untuk pencocokan akses siswa — wajib |
  | `Nomor HP` | dipakai untuk pencocokan akses siswa — wajib |
  | `Nama` | judul laporan |
  | `Kelas` | opsional — kalau ada, tetap dicek cocok sebagai lapis keamanan tambahan (jaga-jaga ada baris yang salah tempel tab) |
  | `Total Persentase Kuis` | angka 0-100 (boleh diisi mis. `82` atau `82%`) |
  | `Total Persentase Kehadiran` | angka 0-100, persentase kehadiran Kelas Zoom |
  | `Catatan` | teks bebas dari wali kelas, opsional — boleh dikosongkan |

  Siswa harus memasukkan **Kelas yang tepat** (supaya tab yang benar terbuka)
  ditambah **Email + Nomor HP** yang cocok persis dengan satu baris di tab itu
  (email dicocokkan tanpa memandang huruf besar/kecil) untuk bisa melihat
  laporannya.

- Contoh data dummy untuk uji coba (isi masing-masing ke tab kelasnya):
  [`data/dummy_semester_2_leadership.csv`](data/dummy_semester_2_leadership.csv)
  (3 baris, untuk tab `Semester 2 Leadership`) dan
  [`data/dummy_semester_2_pastoral.csv`](data/dummy_semester_2_pastoral.csv)
  (5 baris, untuk tab `Semester 2 Pastoral`).

### Status kelulusan dihitung otomatis

Aplikasi **tidak** membaca status lulus/tidak dari kolom manapun di sheet — status
dihitung otomatis dari `Total Persentase Kuis` dan `Total Persentase Kehadiran`
memakai syarat tetap:

- Kehadiran Kelas Zoom minimal **75%**
- Total nilai kuis minimal **70%**

Siswa yang tidak memenuhi salah satu (atau keduanya) akan melihat pesan "Belum
memenuhi syarat kelulusan" lengkap dengan kriteria mana yang kurang — Anda tidak
perlu mengetik status ini secara manual per siswa. Kalau syarat kelulusan berubah
di semester berikutnya, ubah `KEHADIRAN_MIN`/`KUIS_MIN` di bagian atas
[`app.py`](app.py).

**Soal format persen:** kalau kolom `Total Persentase Kuis`/`Total Persentase
Kehadiran` di-format sebagai "Percent" oleh Google Sheets, nilainya akan terbaca
sebagai pecahan (`0.75` untuk 75%) alih-alih `75`. Aplikasi ini sudah menangani
kedua kemungkinan secara otomatis, tapi supaya konsisten sebaiknya format kolom
tersebut sebagai **Number** biasa dan isi angka polos (`75`, bukan `0.75` atau
`"75%"`).

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
2. Buat **dua tab**: `Semester 2 Leadership` dan `Semester 2 Pastoral`. Isi
   baris pertama tiap tab dengan header dari file dummy yang sesuai
   ([`data/dummy_semester_2_leadership.csv`](data/dummy_semester_2_leadership.csv)
   dan [`data/dummy_semester_2_pastoral.csv`](data/dummy_semester_2_pastoral.csv))
   lalu paste data dummy-nya masing-masing untuk uji coba (ingat: format kolom
   Nomor HP sebagai Plain text dulu sebelum paste).
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

## Uji coba dengan data dummy

1. Pastikan tab `Semester 2 Leadership` dan `Semester 2 Pastoral` di
   spreadsheet Anda sudah berisi data dari kedua file dummy (lihat "Struktur
   data" di atas).
2. Jalankan `streamlit run app.py`.
3. Coba kombinasi berikut untuk memverifikasi alur (semua pakai Email + Kelas +
   Nomor HP):
   - `testsatu@example.com` / `MMin 2 Leadership` / `081234500001` → laporan
     "Test Satu" muncul, status **memenuhi syarat kelulusan** (kuis 88%,
     kehadiran 95%).
   - `testdua@example.com` / `MMin 2 Leadership` / `08123 4500 002` (nomor HP
     dengan spasi) → tetap cocok dengan "Test Dua" (menguji normalisasi spasi),
     status **belum memenuhi syarat** karena kehadiran 68% (di bawah 75%)
     meski kuis 82% sudah memenuhi syarat.
   - `testtiga@example.com` / `MMin 2 Pastoral` / `081234500003` → "Test Tiga",
     status **belum memenuhi syarat** karena kuis 65% (di bawah 70%) meski
     kehadiran 90% sudah memenuhi syarat.
   - `testempat@example.com` / `MMin 2 Pastoral` / `081234500004` → "Test
     Empat", status **belum memenuhi syarat** pada kedua kriteria sekaligus.
   - `testenam@example.com` / `MMin 2 Pastoral` / `081234500006` → "Test Enam",
     status **memenuhi syarat kelulusan** (kuis 85%, kehadiran 92%).
   - `testtujuh@example.com` / `MMin 2 Pastoral` / `081234500007` → "Test
     Tujuh", status **belum memenuhi syarat** karena kehadiran 65% (di bawah
     75%) meski kuis 78% sudah memenuhi syarat.
   - `testdelapan@example.com` / `MMin 2 Pastoral` / `+62 812-3450-0008` →
     "Test Delapan" (menguji normalisasi nomor HP format `+62` di tab
     Pastoral), status **memenuhi syarat**.
   - `TestLima@Example.com` (huruf besar/kecil dicampur) / `MMin 2 Leadership` /
     `+62 812-3450-0005` → tetap cocok dengan "Test Lima" (menguji normalisasi
     email dan nomor HP format `+62` sekaligus), status **memenuhi syarat**.
   - `testsatu@example.com` / `MMin 2 Pastoral` (Kelas salah — data Test Satu
     sebenarnya ada di tab Leadership, jadi Apps Script membuka tab Pastoral
     yang tidak punya barisnya) → harus muncul pesan generik "Data tidak
     ditemukan", bukan pesan spesifik.
4. Setelah semua kombinasi di atas berhasil, ganti isi kedua tab dengan data
   120 siswa asli masing-masing (satu baris per siswa, di tab kelasnya).

## Menambah semester baru

Buat **dua tab baru** (satu per kelas) dengan nama bebas asalkan kata
terakhirnya tetap `Leadership`/`Pastoral`, mis. `Semester 1 2027 Leadership`
dan `Semester 1 2027 Pastoral`, isi header + data seperti biasa, lalu
pindahkan keduanya ke urutan **paling kanan** (klik kanan tab → Move right,
atau drag) — asal lebih ke kanan dari tab lama untuk kelas yang sama, urutan
relatif antara tab Leadership dan Pastoral sendiri tidak masalah. Tab lama
tetap ada sebagai arsip dan tidak akan terpakai lagi (bisa butuh sampai 5 menit
untuk efeknya terlihat karena hasil `list_semesters` di-cache) — tidak perlu
ubah kode maupun deploy ulang Apps Script.

## Checklist sebelum deploy

- [ ] Kolom `Total Persentase Kuis`/`Total Persentase Kehadiran` format **Number**
      biasa (bukan Percent) dan kolom `Nomor HP` format **Plain text**.
- [ ] Semua 5 skenario uji di atas sudah dicoba dan hasilnya benar.
- [ ] Data dummy sudah diganti dengan data 240 siswa asli, dan **setiap baris
      dicek tidak ada Email/Nomor HP yang kosong atau duplikat** (kalau ada
      dua siswa dengan Email+Kelas+Nomor HP identik, hanya baris pertama yang
      pernah cocok yang akan ketemu — cek dengan fitur "Highlight duplicates"
      Google Sheets atau filter manual).
- [ ] Nama tab diakhiri kata `Leadership`/`Pastoral` sesuai isinya, dan data
      120 siswa masing-masing sudah masuk ke tab kelasnya yang benar (bukan
      tertukar). Kalau kolom `Kelas` masih dipakai di tiap baris, isinya
      **persis** `MMin 2 Leadership` atau `MMin 2 Pastoral` — hindari typo
      seperti "Mmin 2 leadership " dengan spasi tambahan.
- [ ] `.streamlit/secrets.toml` **tidak** ikut ter-commit ke Git (`git status`
      setelah `git add` — pastikan tidak ada baris `secrets.toml`).
- [ ] Repo GitHub tujuan deploy sudah **public**.
- [ ] Coba buka Web App URL Apps Script langsung di browser (`.../exec`) — kalau
      muncul `{"ok":true,...}` berarti deployment aktif dan bisa diakses publik.

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
