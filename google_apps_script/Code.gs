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
var COLUMN_NAMA = 'nama';

// Tab log akses siswa -- dibuat otomatis saat pertama kali dibutuhkan.
var ACCESS_LOG_SHEET_NAME = '_AccessLog';
var ACCESS_LOG_HEADERS = ['Timestamp', 'Nama', 'Email', 'Kelas', 'Semester'];

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
      case 'admin_list_class':
        return jsonResponse(adminListClass(body.kelas));
      case 'admin_save_class':
        return jsonResponse(adminSaveClass(body.kelas, body.rows));
      case 'admin_access_log':
        return jsonResponse(adminAccessLog());
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
  var namaIdx = findColumn(headers, COLUMN_NAMA);
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
      var semesterLabel = displaySemesterLabel(sheet.getName(), kelas);
      logAccess(kelas, semesterLabel, namaIdx !== -1 ? row[namaIdx] : '', email);
      return { ok: true, semester: semesterLabel, data: data };
    }
  }

  return { ok: false, message: 'Data tidak ditemukan.' };
}

/**
 * Catat satu kejadian "siswa berhasil melihat laporannya" ke tab _AccessLog
 * (dibuat otomatis kalau belum ada). Dibungkus try/catch supaya kalau gagal
 * menulis log, siswa tetap bisa melihat laporannya seperti biasa.
 */
function logAccess(kelas, semesterLabel, nama, email) {
  try {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = ss.getSheetByName(ACCESS_LOG_SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(ACCESS_LOG_SHEET_NAME);
      sheet.appendRow(ACCESS_LOG_HEADERS);
    }
    sheet.appendRow([new Date(), nama, email, kelas, semesterLabel]);
  } catch (err) {
    console.error('logAccess error: ' + err);
  }
}

/**
 * Admin: ambil seluruh baris pada tab kelas aktif (bukan cuma satu baris
 * seperti getReport) supaya bisa ditampilkan sebagai tabel yang bisa diedit.
 * Hanya dipanggil dari panel admin yang sudah dilindungi password di sisi
 * Streamlit -- SHARED_SECRET tetap jadi lapis proteksi utama di sini.
 */
function adminListClass(kelas) {
  if (!kelas) return { ok: false, message: 'Kelas wajib diisi.' };
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };

  var values = sheet.getDataRange().getValues();
  var headers = values.length > 0 ? values[0].map(function (h) { return String(h).trim(); }) : [];
  var rows = [];
  for (var r = 1; r < values.length; r++) {
    var rowObj = {};
    for (var c = 0; c < headers.length; c++) {
      if (!headers[c]) continue;
      rowObj[headers[c]] = values[r][c];
    }
    rows.push(rowObj);
  }
  return { ok: true, sheetName: sheet.getName(), headers: headers, rows: rows };
}

/**
 * Admin: timpa semua baris data (di bawah header) pada tab kelas aktif
 * dengan `rows` yang baru -- dipakai oleh tabel-edit & upload CSV di panel
 * admin. Kolom Nomor HP dipaksa berformat teks supaya angka 0 di depan
 * tidak hilang.
 */
function adminSaveClass(kelas, rows) {
  if (!kelas || !rows) return { ok: false, message: 'Data tidak lengkap.' };
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };

  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  if (lastCol === 0) return { ok: false, message: 'Sheet belum punya header.' };

  var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(function (h) {
    return String(h).trim();
  });

  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, lastCol).clearContent();
  }

  if (rows.length === 0) {
    return { ok: true, savedRows: 0 };
  }

  var phoneColIdx = findColumn(headers, COLUMN_PHONE);
  if (phoneColIdx !== -1) {
    sheet.getRange(2, phoneColIdx + 1, rows.length, 1).setNumberFormat('@');
  }

  var output = rows.map(function (row) {
    return headers.map(function (h) {
      var v = row[h];
      return v === undefined || v === null ? '' : v;
    });
  });

  sheet.getRange(2, 1, output.length, headers.length).setValues(output);
  return { ok: true, savedRows: output.length };
}

/**
 * Admin: ambil seluruh catatan _AccessLog (siapa membuka laporan, kapan).
 * Agregasi per-siswa (jumlah akses, terakhir diakses) dilakukan di sisi
 * Streamlit, bukan di sini, supaya Apps Script-nya tetap sederhana.
 */
function adminAccessLog() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(ACCESS_LOG_SHEET_NAME);
  if (!sheet) return { ok: true, rows: [] };

  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return { ok: true, rows: [] };

  var headers = values[0].map(function (h) { return String(h).trim(); });
  var rows = [];
  for (var r = 1; r < values.length; r++) {
    var obj = {};
    for (var c = 0; c < headers.length; c++) {
      var v = values[r][c];
      if (Object.prototype.toString.call(v) === '[object Date]') {
        v = v.toISOString();
      }
      obj[headers[c]] = v;
    }
    rows.push(obj);
  }
  return { ok: true, rows: rows };
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
