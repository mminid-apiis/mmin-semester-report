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
        return jsonResponse(getReport(body.kelas, body.phone, body.semester));
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
 * Setiap tab pada spreadsheet = satu semester/periode.
 * Tab dengan nama diawali "_" dianggap konfigurasi/internal dan disembunyikan dari daftar.
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

function getReport(kelas, phone, semesterName) {
  if (!kelas || !phone || !semesterName) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(semesterName);
  if (!sheet) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var headers = values[0].map(function (h) { return String(h).trim(); });
  var kelasIdx = findColumn(headers, COLUMN_KELAS);
  var phoneIdx = findColumn(headers, COLUMN_PHONE);

  if (kelasIdx === -1 || phoneIdx === -1) {
    console.error('Sheet "' + semesterName + '" tidak punya kolom "Kelas" atau "Nomor HP".');
    return { ok: false, message: 'Data tidak ditemukan.' };
  }

  var targetKelas = String(kelas).trim().toLowerCase();
  var targetPhone = normalizePhone(phone);

  for (var r = 1; r < values.length; r++) {
    var row = values[r];
    var rowKelas = String(row[kelasIdx]).trim().toLowerCase();
    var rowPhone = normalizePhone(row[phoneIdx]);

    if (rowKelas === targetKelas && rowPhone === targetPhone && rowPhone !== '') {
      var data = {};
      for (var c = 0; c < headers.length; c++) {
        if (!headers[c]) continue;
        data[headers[c]] = row[c];
      }
      return { ok: true, semester: semesterName, data: data };
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
