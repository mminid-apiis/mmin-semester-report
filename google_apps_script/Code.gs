/**
 * MMin Semester Report — backend Apps Script.
 *
 * Deploy sebagai Web App:
 *   Execute as: Me
 *   Who has access: Anyone
 *
 * Setiap kali file ini diubah, WAJIB buat versi baru agar perubahan aktif:
 *   Deploy -> Manage deployments -> Edit (pensil) -> Version: New version -> Deploy
 */

// GANTI dengan ID spreadsheet (bagian URL setelah /d/, SEBELUM /edit), BUKAN URL lengkap.
var SPREADSHEET_ID = 'GANTI_DENGAN_SPREADSHEET_ID';

// GANTI dengan nilai apps_script_secret yang ada di .streamlit/secrets.toml, harus SAMA PERSIS.
var SHARED_SECRET = 'GANTI_DENGAN_SHARED_SECRET';

// Kolom wajib ada di baris pertama setiap tab semester (tidak case-sensitive).
var COLUMN_KELAS = 'kelas';
var COLUMN_PHONE = 'nomor hp';
var COLUMN_EMAIL = 'email';

function doGet(e) {
  return jsonResponse({ ok: true, message: 'MMin Semester Report backend is running.' });
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
  } catch (err) {
    return jsonResponse({ ok: false, message: 'Body request tidak valid.' });
  }

  if (!body || body.secret !== SHARED_SECRET) {
    return jsonResponse({ ok: false, message: 'Unauthorized.' });
  }

  try {
    switch (body.action) {
      case 'ping':
        return jsonResponse({ ok: true, message: 'pong' });
      case 'list_semesters':
        return jsonResponse(listSemesters());
      case 'get_report':
        return jsonResponse(getReport(body.kelas, body.phone, body.email));
      default:
        return jsonResponse({ ok: false, message: 'Action tidak dikenal.' });
    }
  } catch (err) {
    // Detail error hanya masuk log Apps Script (Executions), tidak dikirim ke klien.
    console.error('doPost error: ' + err);
    return jsonResponse({ ok: false, message: 'Terjadi kesalahan di server.' });
  }
}

/**
 * Availability check dipakai frontend untuk tahu apakah spreadsheet punya
 * tab yang bisa dibaca sama sekali (bukan lagi daftar pilihan semester —
 * semester tidak lagi dipilih siswa, lihat findClassSheet()).
 * Tab dengan nama diawali "_" dianggap konfigurasi/internal dan disembunyikan.
 */
function listSemesters() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheets = ss.getSheets();
  var names = [];
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (name.indexOf('_') === 0) continue;
    names.push(name);
  }
  return { ok: true, semesters: names };
}

/**
 * Satu tab = satu kelas untuk satu periode, mis. "Semester 2 Leadership" dan
 * "Semester 2 Pastoral". Dicari berdasarkan kata terakhir pada nilai Kelas
 * (mis. "MMin 2 Leadership" -> kata kunci "leadership") sebagai substring
 * nama tab (tidak case-sensitive). Kalau ada beberapa tab yang cocok untuk
 * kelas yang sama (semester lama masih disimpan sebagai arsip), yang dipakai
 * adalah tab PALING KANAN (terbaru) di antara yang cocok itu.
 */
function findClassSheet(ss, kelas) {
  var parts = String(kelas).trim().split(/\s+/);
  var keyword = parts[parts.length - 1].toLowerCase();
  if (!keyword) return null;

  var sheets = ss.getSheets();
  var match = null;
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (name.indexOf('_') === 0) continue;
    if (name.toLowerCase().indexOf(keyword) !== -1) {
      match = sheets[i];
    }
  }
  return match;
}

/**
 * Label semester yang ditampilkan ke siswa: nama tab dengan kata kelas di
 * akhir dibuang, mis. "Semester 2 Leadership" -> "Semester 2".
 */
function displaySemesterLabel(sheetName, kelas) {
  var parts = String(kelas).trim().split(/\s+/);
  var keyword = parts[parts.length - 1];
  if (!keyword) return sheetName;
  var re = new RegExp('\\s*' + keyword + '\\s*$', 'i');
  var label = sheetName.replace(re, '').trim();
  return label || sheetName;
}

function getReport(kelas, phone, email) {
  if (!kelas || !phone || !email) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var headers = values[0].map(function (h) { return String(h).trim(); });
  var phoneIdx = findColumn(headers, COLUMN_PHONE);
  var emailIdx = findColumn(headers, COLUMN_EMAIL);
  // Kolom Kelas opsional di sini: tab-nya sendiri sudah memilah per kelas,
  // tapi kalau kolom ini ada, tetap dicek sebagai lapis keamanan tambahan
  // (jaga-jaga ada baris yang salah tempel tab).
  var kelasIdx = findColumn(headers, COLUMN_KELAS);

  if (phoneIdx === -1 || emailIdx === -1) {
    console.error('Sheet "' + sheet.getName() + '" tidak punya kolom "Nomor HP" atau "Email".');
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var targetKelas = String(kelas).trim().toLowerCase();
  var targetPhone = normalizePhone(phone);
  var targetEmail = String(email).trim().toLowerCase();

  for (var r = 1; r < values.length; r++) {
    var row = values[r];
    var rowPhone = normalizePhone(row[phoneIdx]);
    var rowEmail = String(row[emailIdx]).trim().toLowerCase();
    var kelasOk = true;
    if (kelasIdx !== -1) {
      kelasOk = String(row[kelasIdx]).trim().toLowerCase() === targetKelas;
    }

    if (kelasOk && rowPhone === targetPhone && rowPhone !== '' && rowEmail === targetEmail && rowEmail !== '') {
      var data = {};
      for (var c = 0; c < headers.length; c++) {
        if (!headers[c]) continue;
        data[headers[c]] = row[c];
      }
      return { ok: true, semester: displaySemesterLabel(sheet.getName(), kelas), data: data };
    }
  }

  return { ok: false, message: 'Data tidak ditemukan.' };
}

function findColumn(headers, wantedLower) {
  for (var i = 0; i < headers.length; i++) {
    if (headers[i].toLowerCase() === wantedLower) return i;
  }
  return -1;
}

/**
 * Normalisasi nomor HP ke format "08xxxxxxxxxx" sebelum dibandingkan.
 * - Hapus spasi, strip, tanda kurung.
 * - "+62xxx" atau "62xxx" -> "0xxx".
 * - Sudah "0xxx" -> dibiarkan.
 * - Jaga-jaga: Google Sheets kadang menyimpan Nomor HP sebagai angka dan
 *   menghapus angka 0 di depan (mis. "08123456789" jadi 8123456789). Kalau
 *   hasilnya semua angka tapi tidak diawali 0, tambahkan kembali 0 di depan.
 */
function normalizePhone(raw) {
  if (raw === null || raw === undefined || raw === '') return '';
  var s = String(raw).trim();
  s = s.replace(/[\s\-()]/g, '');

  if (s.indexOf('+62') === 0) {
    s = '0' + s.substring(3);
  } else if (s.indexOf('62') === 0) {
    s = '0' + s.substring(2);
  } else if (s.indexOf('0') !== 0 && /^[0-9]+$/.test(s)) {
    s = '0' + s;
  }

  return s;
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
