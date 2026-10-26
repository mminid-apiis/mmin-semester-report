/**
 * MMin Semester Report — backend Apps Script.
 *
 * Deploy sebagai Web App:
 *   Execute as: Me
 *   Who has access: Anyone
 *
 * Setiap kali file ini diubah, WAJIB buat versi baru agar perubahan aktif:
 *   Deploy -> Manage deployments -> Edit (pensil) -> Version: New version -> Deploy
 *
 * Fitur notifikasi email butuh izin tambahan (kirim email). Setelah menempel
 * versi ini, pilih fungsi `authorizeScopes` di dropdown editor, klik Run, dan
 * setujui izinnya SEKALI -- baru setelah itu deploy versi baru.
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
var COLUMN_KUIS = 'total persentase kuis';

// Tab log akses siswa -- satu tab per kelas, dibuat otomatis saat pertama
// kali dibutuhkan (mis. "_AccessLog_Leadership", "_AccessLog_Pastoral").
var ACCESS_LOG_PREFIX = '_AccessLog_';
var ACCESS_LOG_HEADERS = ['Timestamp', 'Nama', 'Email', 'Kelas', 'Semester'];

// Zona waktu dipakai saat menampilkan Timestamp log akses ke admin.
var DISPLAY_TIMEZONE = 'Asia/Jakarta';

// Log aktivitas admin (login, logout, ubah nilai, kirim email) -- satu tab
// untuk semua kelas, dibuat otomatis saat pertama kali dibutuhkan.
var ADMIN_AUDIT_SHEET = '_AdminAuditLog';
var ADMIN_AUDIT_HEADERS = [
  'Timestamp', 'Admin', 'Aksi', 'Kelas', 'Siswa (Email)', 'Kolom', 'Nilai Lama', 'Nilai Baru', 'Keterangan'
];
// Event yang boleh dicatat langsung dari Streamlit lewat admin_log_event.
var ADMIN_EVENTS = ['login', 'login_gagal', 'logout'];
// Batas jumlah baris "ubah_nilai" per sekali simpan (sisanya diringkas) dan
// jumlah baris log yang dikirim balik ke panel admin.
var ADMIN_AUDIT_MAX_CHANGE_ROWS = 1500;
var ADMIN_AUDIT_MAX_RETURN_ROWS = 5000;
// Isi kolom ini tidak ditulis apa adanya ke log (hanya "(disembunyikan)").
var AUDIT_MASKED_COLUMNS = ['nomor hp'];

// Notifikasi email ke siswa (lihat adminNotifySend).
var NOTIF_LOG_SHEET = '_NotifLog';
var NOTIF_LOG_HEADERS = ['Timestamp', 'Admin', 'Kelas', 'Semester', 'Email', 'Jenis', 'Status'];
var NOTIF_STATUS_SENT = 'terkirim';
// Jumlah email per sekali panggilan (Streamlit memanggil berulang sampai habis).
var NOTIF_BATCH_SIZE = 30;
// Pengingat tidak dikirim lagi ke siswa yang sudah diingatkan dalam jangka ini.
var REMINDER_COOLDOWN_HOURS = 48;
// Link yang dicantumkan di email -- ubah di sini kalau alamat aplikasi berubah.
var PORTAL_URL = 'https://mmin-semester-report.streamlit.app/';
var MAIL_SENDER_NAME = 'APIIS MMin';

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
        return jsonResponse(adminSaveClass(body.kelas, body.rows, body.admin, body.baseVersion));
      case 'admin_access_log':
        return jsonResponse(adminAccessLog());
      case 'admin_log_event':
        return jsonResponse(adminLogEvent(body.admin, body.event, body.detail));
      case 'admin_audit_log':
        return jsonResponse(adminAuditLog());
      case 'admin_notify_status':
        return jsonResponse(adminNotifyStatus(body.kelas, body.force));
      case 'admin_notify_send':
        return jsonResponse(adminNotifySend(body.kelas, body.jenis, body.admin, body.force, body.exclude));
      case 'admin_notify_test':
        return jsonResponse(adminNotifyTest(body.kelas, body.jenis, body.admin));
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
      var rank = computeQuizRank(values, headers, r, targetKelas);
      return { ok: true, semester: semesterLabel, data: data, rank: rank };
    }
  }

  return { ok: false, message: 'Data tidak ditemukan.' };
}

/**
 * Sama dengan parse_percentage() di app_pages/student.py: angka biasa (75),
 * teks ("75%"), atau pecahan hasil format Percent di Sheets (0.75) -> skala 0-100.
 * Hasilnya dibulatkan 2 desimal supaya nilai yang sama selalu dianggap seri.
 */
function parsePercentage(value) {
  if (value === null || value === undefined || value === '') return null;
  var num;
  if (typeof value === 'number') {
    num = value;
  } else {
    var text = String(value).trim().replace('%', '').replace(',', '.');
    if (!text) return null;
    num = Number(text);
    if (isNaN(num)) return null;
  }
  if (num >= 0 && num <= 1) num = num * 100;
  return Math.round(num * 100) / 100;
}

/**
 * Peringkat siswa (baris `myRow`) di kelasnya berdasarkan Total Persentase Kuis.
 * Dihitung di sini (bukan di Streamlit) supaya nilai siswa lain tidak pernah
 * dikirim ke browser -- yang keluar hanya {position, total}.
 *  - Yang dihitung: baris yang punya Nama atau Email dan punya nilai kuis angka,
 *    dan (kalau kolom Kelas ada) Kelas-nya sama dengan kelas yang dipilih.
 *  - Seri berbagi peringkat yang sama (1, 2, 2, 4): peringkat = 1 + jumlah siswa
 *    yang nilainya LEBIH tinggi.
 *  - Mengembalikan null kalau kolom kuis tidak ada atau nilai kuis siswa ini kosong.
 */
function computeQuizRank(values, headers, myRow, targetKelas) {
  var kuisIdx = findColumn(headers, COLUMN_KUIS);
  if (kuisIdx === -1) return null;
  var mine = parsePercentage(values[myRow][kuisIdx]);
  if (mine === null) return null;

  var emailIdx = findColumn(headers, COLUMN_EMAIL);
  var namaIdx = findColumn(headers, COLUMN_NAMA);
  var kelasIdx = findColumn(headers, COLUMN_KELAS);

  var total = 0;
  var higher = 0;
  for (var r = 1; r < values.length; r++) {
    var hasIdentity = (emailIdx !== -1 && cellText(values[r][emailIdx]) !== '') ||
                      (namaIdx !== -1 && cellText(values[r][namaIdx]) !== '');
    if (!hasIdentity) continue;
    if (kelasIdx !== -1 && cellText(values[r][kelasIdx]).toLowerCase() !== targetKelas) continue;
    var score = parsePercentage(values[r][kuisIdx]);
    if (score === null) continue;
    total++;
    if (score > mine) higher++;
  }
  return { position: higher + 1, total: total };
}

/**
 * Nama tab log akses untuk satu kelas, mis. "MMin 2 Leadership" ->
 * "_AccessLog_Leadership". Sama seperti findClassSheet(), berdasar kata
 * terakhir pada nilai Kelas.
 */
function accessLogSheetName(kelas) {
  var parts = String(kelas).trim().split(/\s+/);
  var keyword = parts[parts.length - 1];
  return ACCESS_LOG_PREFIX + keyword;
}

/**
 * Catat satu kejadian "siswa berhasil melihat laporannya" ke tab log akses
 * kelas terkait (dibuat otomatis kalau belum ada). Dibungkus try/catch
 * supaya kalau gagal menulis log, siswa tetap bisa melihat laporannya
 * seperti biasa.
 */
function logAccess(kelas, semesterLabel, nama, email) {
  try {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheetName = accessLogSheetName(kelas);
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
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
  var parsed = valuesToRows(values);
  // `version` = sidik jari isi tab saat ini; dikirim balik saat menyimpan
  // supaya perubahan admin lain di antaranya bisa terdeteksi (adminSaveClass).
  return {
    ok: true,
    sheetName: sheet.getName(),
    headers: parsed.headers,
    rows: parsed.rows,
    version: dataVersion(values)
  };
}

function valuesToRows(values) {
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
  return { headers: headers, rows: rows };
}

function dataVersion(values) {
  var digest = Utilities.computeDigest(
    Utilities.DigestAlgorithm.MD5,
    JSON.stringify(values),
    Utilities.Charset.UTF_8
  );
  return digest.map(function (b) {
    return ('0' + (b & 0xff).toString(16)).slice(-2);
  }).join('');
}

/**
 * Admin: timpa semua baris data (di bawah header) pada tab kelas aktif
 * dengan `rows` yang baru -- dipakai oleh tabel-edit & upload CSV di panel
 * admin. Kolom Nomor HP dipaksa berformat teks supaya angka 0 di depan
 * tidak hilang.
 *
 * - `admin`: nama akun admin yang menyimpan (dicatat ke log aktivitas admin).
 * - `baseVersion`: `version` dari adminListClass saat data dimuat. Kalau
 *   isi tab sudah berubah sejak itu (mis. admin lain menyimpan lebih dulu),
 *   simpan ditolak dengan code 'conflict' supaya tidak menimpa pekerjaan
 *   orang lain. Kosong = tidak dicek (kompatibel dengan klien lama).
 * - Setiap perubahan (sel diubah / siswa ditambah / siswa dihapus) dicatat ke
 *   tab _AdminAuditLog. Isi kolom Nomor HP tidak dicatat apa adanya.
 */
function adminSaveClass(kelas, rows, admin, baseVersion) {
  if (!kelas || !rows) return { ok: false, message: 'Data tidak lengkap.' };
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };
  var adminName = cleanAdminName(admin);

  return withScriptLock(function () {
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    if (lastCol === 0) return { ok: false, message: 'Sheet belum punya header.' };

    var current = sheet.getDataRange().getValues();
    if (baseVersion && baseVersion !== dataVersion(current)) {
      appendLogRows(ADMIN_AUDIT_SHEET, ADMIN_AUDIT_HEADERS, [[
        new Date(), adminName, 'simpan_ditolak', kelas, '', '', '', '',
        'Data di sheet sudah berubah sejak dimuat (kemungkinan admin lain menyimpan lebih dulu).'
      ]]);
      return {
        ok: false,
        code: 'conflict',
        message: 'Data di sheet sudah berubah sejak Anda memuatnya.'
      };
    }

    var parsed = valuesToRows(current);
    var headers = parsed.headers;
    var changes = diffClassRows(headers, parsed.rows, rows);

    if (lastRow > 1) {
      sheet.getRange(2, 1, lastRow - 1, lastCol).clearContent();
    }

    if (rows.length > 0) {
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
    }
    SpreadsheetApp.flush();

    appendLogRows(
      ADMIN_AUDIT_SHEET,
      ADMIN_AUDIT_HEADERS,
      buildSaveAuditRows(adminName, kelas, changes, rows.length, parsed.rows.length)
    );

    return {
      ok: true,
      savedRows: rows.length,
      version: dataVersion(sheet.getDataRange().getValues()),
      changes: changes.counts
    };
  });
}

function cleanAdminName(name) {
  var s = String(name === undefined || name === null ? '' : name).trim().substring(0, 40);
  return safeCell(s || '(tidak diketahui)');
}

function cellText(v) {
  return v === undefined || v === null ? '' : String(v).trim();
}

// Cegah teks yang diawali = + - @ dibaca Sheets sebagai rumus saat ditulis ke log.
function safeCell(v) {
  if (typeof v === 'string' && /^[=+\-@]/.test(v)) return "'" + v;
  return v;
}

function withScriptLock(fn) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    return fn();
  } finally {
    lock.releaseLock();
  }
}

function getOrCreateLogSheet(ss, name, headers) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name, ss.getNumSheets());
    sheet.appendRow(headers);
  }
  return sheet;
}

function appendLogRows(name, headers, rows) {
  if (!rows.length) return;
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = getOrCreateLogSheet(ss, name, headers);
  var start = sheet.getLastRow() + 1;
  sheet.getRange(start, 1, rows.length, headers.length).setValues(rows);
}

/**
 * Bandingkan isi tab sebelum (oldRows) dan sesudah (newRows) disimpan.
 * Siswa dikenali lewat Email (huruf kecil); kalau Email kosong, lewat Nama;
 * kalau keduanya kosong atau ada yang kembar, lewat nomor urut baris.
 */
function diffClassRows(headers, oldRows, newRows) {
  var emailIdx = findColumn(headers, COLUMN_EMAIL);
  var namaIdx = findColumn(headers, COLUMN_NAMA);
  var emailHeader = emailIdx === -1 ? null : headers[emailIdx];
  var namaHeader = namaIdx === -1 ? null : headers[namaIdx];

  function keysFor(rows) {
    var seen = {};
    return rows.map(function (row, i) {
      var key = emailHeader ? cellText(row[emailHeader]).toLowerCase() : '';
      if (!key) {
        var nama = namaHeader ? cellText(row[namaHeader]).toLowerCase() : '';
        key = nama ? '#' + nama : '#baris' + (i + 1);
      }
      if (seen[key]) {
        seen[key]++;
        key = key + '#' + seen[key];
      } else {
        seen[key] = 1;
      }
      return key;
    });
  }

  var oldKeys = keysFor(oldRows);
  var newKeys = keysFor(newRows);
  var oldMap = {};
  var newMap = {};
  oldKeys.forEach(function (k, i) { oldMap[k] = oldRows[i]; });
  newKeys.forEach(function (k, i) { newMap[k] = newRows[i]; });

  var list = [];
  var counts = { ubah: 0, tambah: 0, hapus: 0 };

  function identity(row, key) {
    return {
      email: emailHeader ? cellText(row[emailHeader]) : '',
      nama: namaHeader ? cellText(row[namaHeader]) : '',
      key: key
    };
  }

  newKeys.forEach(function (key, i) {
    var newRow = newRows[i];
    var who = identity(newRow, key);
    if (!Object.prototype.hasOwnProperty.call(oldMap, key)) {
      counts.tambah++;
      list.push({ aksi: 'tambah_siswa', email: who.email, nama: who.nama, kolom: '', lama: '', baru: '' });
      return;
    }
    var oldRow = oldMap[key];
    headers.forEach(function (h) {
      if (!h) return;
      var oldV = cellText(oldRow[h]);
      var newV = cellText(newRow[h]);
      if (oldV === newV) return;
      var masked = AUDIT_MASKED_COLUMNS.indexOf(h.toLowerCase()) !== -1;
      counts.ubah++;
      list.push({
        aksi: 'ubah_nilai',
        email: who.email,
        nama: who.nama,
        kolom: h,
        lama: masked ? '(disembunyikan)' : oldV,
        baru: masked ? '(disembunyikan)' : newV
      });
    });
  });

  oldKeys.forEach(function (key, i) {
    if (Object.prototype.hasOwnProperty.call(newMap, key)) return;
    var who = identity(oldRows[i], key);
    counts.hapus++;
    list.push({ aksi: 'hapus_siswa', email: who.email, nama: who.nama, kolom: '', lama: '', baru: '' });
  });

  return { list: list, counts: counts };
}

function buildSaveAuditRows(adminName, kelas, changes, newTotal, oldTotal) {
  var now = new Date();
  var c = changes.counts;
  var summary = c.ubah + c.tambah + c.hapus === 0
    ? 'Tanpa perubahan (' + newTotal + ' baris).'
    : 'Ubah ' + c.ubah + ' sel, tambah ' + c.tambah + ' siswa, hapus ' + c.hapus +
      ' siswa. Total ' + newTotal + ' baris (sebelumnya ' + oldTotal + ').';
  var out = [[now, adminName, 'simpan_nilai', kelas, '', '', '', '', summary]];

  var shown = changes.list.slice(0, ADMIN_AUDIT_MAX_CHANGE_ROWS);
  shown.forEach(function (ch) {
    out.push([
      now, adminName, ch.aksi, kelas,
      safeCell(ch.email), safeCell(ch.kolom), safeCell(ch.lama), safeCell(ch.baru),
      safeCell(ch.nama)
    ]);
  });
  if (changes.list.length > shown.length) {
    out.push([
      now, adminName, 'simpan_nilai', kelas, '', '', '', '',
      '... dan ' + (changes.list.length - shown.length) + ' perubahan lain tidak dirinci.'
    ]);
  }
  return out;
}

/**
 * Admin: catat login/logout/login gagal (dipanggil dari Streamlit, yang
 * memverifikasi password). Hanya event di ADMIN_EVENTS yang diterima.
 */
function adminLogEvent(admin, event, detail) {
  if (ADMIN_EVENTS.indexOf(event) === -1) return { ok: false, message: 'Event tidak dikenal.' };
  withScriptLock(function () {
    appendLogRows(ADMIN_AUDIT_SHEET, ADMIN_AUDIT_HEADERS, [[
      new Date(), cleanAdminName(admin), event, '', '', '', '', '',
      safeCell(String(detail || '').substring(0, 200))
    ]]);
  });
  return { ok: true };
}

/** Admin: log aktivitas admin (paling baru di akhir), dibatasi ADMIN_AUDIT_MAX_RETURN_ROWS. */
function adminAuditLog() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(ADMIN_AUDIT_SHEET);
  if (!sheet) return { ok: true, rows: [] };
  var rows = readAccessLogSheet(sheet);
  if (rows.length > ADMIN_AUDIT_MAX_RETURN_ROWS) {
    rows = rows.slice(rows.length - ADMIN_AUDIT_MAX_RETURN_ROWS);
  }
  return { ok: true, rows: rows };
}

/**
 * Admin: ambil seluruh catatan log akses dari SEMUA tab "_AccessLog_*"
 * (satu tab per kelas) sekaligus, digabung jadi satu daftar -- kolom Kelas
 * di tiap baris sudah cukup untuk memilah per kelas di sisi Streamlit.
 * Timestamp diformat ke zona waktu Asia/Jakarta (WIB) supaya tidak
 * membingungkan (nilai aslinya tersimpan sebagai Date, bukan UTC/lokal
 * tertentu -- ini murni soal bagaimana menampilkannya).
 */
function adminAccessLog() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheets = ss.getSheets();
  var rows = [];
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (name.indexOf(ACCESS_LOG_PREFIX) !== 0) continue;
    rows = rows.concat(readAccessLogSheet(sheets[i]));
  }
  return { ok: true, rows: rows };
}

function readAccessLogSheet(sheet) {
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];

  var headers = values[0].map(function (h) { return String(h).trim(); });
  var rows = [];
  for (var r = 1; r < values.length; r++) {
    var obj = {};
    for (var c = 0; c < headers.length; c++) {
      var v = values[r][c];
      if (Object.prototype.toString.call(v) === '[object Date]') {
        v = Utilities.formatDate(v, DISPLAY_TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
      }
      obj[headers[c]] = v;
    }
    rows.push(obj);
  }
  return rows;
}

// ---------------------------------------------------------------------------
// Notifikasi email ke siswa
//
// Hanya dijalankan atas permintaan admin dari panel Admin. Email SELALU hanya
// berisi link ke aplikasi dan cara membukanya -- tidak pernah memuat nilai,
// status lulus, atau syarat kelulusan. Penerima dipilih di sini, bukan dikirim
// dari klien, dan hanya siswa yang ada di tab kelas dengan email valid.
// ---------------------------------------------------------------------------

/** Jalankan SEKALI dari editor Apps Script (tombol Run) untuk memberi izin kirim email. */
function authorizeScopes() {
  MailApp.getRemainingDailyQuota();
  Session.getEffectiveUser().getEmail();
  LockService.getScriptLock();
  SpreadsheetApp.openById(SPREADSHEET_ID);
}

function emailLooksValid(s) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

function readSheetObjects(sheet) {
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  var headers = values[0].map(function (h) { return String(h).trim(); });
  var rows = [];
  for (var r = 1; r < values.length; r++) {
    var obj = {};
    for (var c = 0; c < headers.length; c++) obj[headers[c]] = values[r][c];
    rows.push(obj);
  }
  return rows;
}

/** Kumpulkan data yang dibutuhkan untuk menentukan siapa yang layak dikirimi email. */
function buildNotifyContext(ss, kelas) {
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) return null;
  var semester = displaySemesterLabel(sheet.getName(), kelas);

  var values = sheet.getDataRange().getValues();
  var parsed = valuesToRows(values);
  var emailIdx = findColumn(parsed.headers, COLUMN_EMAIL);
  var namaIdx = findColumn(parsed.headers, COLUMN_NAMA);
  var emailHeader = emailIdx === -1 ? null : parsed.headers[emailIdx];
  var namaHeader = namaIdx === -1 ? null : parsed.headers[namaIdx];

  var students = [];
  var invalid = [];
  var seen = {};
  parsed.rows.forEach(function (row) {
    var email = emailHeader ? cellText(row[emailHeader]) : '';
    var nama = namaHeader ? cellText(row[namaHeader]) : '';
    if (!email && !nama) return;
    if (!emailLooksValid(email)) {
      invalid.push(nama || '(tanpa nama)');
      return;
    }
    var key = email.toLowerCase();
    if (seen[key]) return;
    seen[key] = true;
    students.push({ nama: nama, email: email });
  });

  // Siapa yang sudah menerima email jenis apa (khusus kelas + semester ini).
  var sent = {};
  var notifSheet = ss.getSheetByName(NOTIF_LOG_SHEET);
  if (notifSheet) {
    readSheetObjects(notifSheet).forEach(function (r) {
      if (r['Kelas'] !== kelas || r['Semester'] !== semester || r['Status'] !== NOTIF_STATUS_SENT) return;
      var key = cellText(r['Email']).toLowerCase();
      var jenis = cellText(r['Jenis']);
      var ts = r['Timestamp'] instanceof Date ? r['Timestamp'].getTime() : 0;
      if (!sent[key]) sent[key] = {};
      if (!sent[key][jenis] || sent[key][jenis] < ts) sent[key][jenis] = ts;
    });
  }

  // Siapa yang sudah membuka laporan SEMESTER INI (log akses menyimpan semester).
  var opened = {};
  var accessSheet = ss.getSheetByName(accessLogSheetName(kelas));
  if (accessSheet) {
    readSheetObjects(accessSheet).forEach(function (r) {
      if (r['Semester'] !== semester) return;
      opened[cellText(r['Email']).toLowerCase()] = true;
    });
  }

  return { sheet: sheet, semester: semester, students: students, invalid: invalid, sent: sent, opened: opened };
}

/**
 * Tentukan siapa yang akan dikirimi email `jenis` ('baru' atau 'pengingat').
 * Sumber kebenaran tunggal: dipakai untuk pratinjau (adminNotifyStatus) maupun
 * pengiriman sungguhan (adminNotifySend), jadi keduanya selalu konsisten.
 *  - baru: lewati siswa yang sudah pernah menerima email "baru" semester ini.
 *  - pengingat: lewati siswa yang sudah membuka laporan semester ini, dan yang
 *    sudah diingatkan dalam REMINDER_COOLDOWN_HOURS terakhir.
 * `force` mengabaikan "sudah dikirim"/"baru diingatkan" (bukan "sudah membuka").
 */
function planNotification(ctx, jenis, force) {
  var eligible = [];
  var skipped = [];
  var cooldownMs = REMINDER_COOLDOWN_HOURS * 3600 * 1000;
  var now = new Date().getTime();

  ctx.students.forEach(function (s) {
    var key = s.email.toLowerCase();
    var mine = ctx.sent[key] || {};
    var reason = '';
    if (jenis === 'baru') {
      if (mine.baru && !force) reason = 'sudah_dikirim';
    } else {
      if (ctx.opened[key]) reason = 'sudah_membuka';
      else if (mine.pengingat && !force && now - mine.pengingat < cooldownMs) reason = 'baru_diingatkan';
    }
    if (reason) skipped.push({ nama: s.nama, email: s.email, reason: reason });
    else eligible.push({ nama: s.nama, email: s.email });
  });

  return { eligible: eligible, skipped: skipped };
}

function renderEmail(jenis, nama, kelas, semester) {
  var url = PORTAL_URL;
  var reminder = jenis === 'pengingat';
  var greetId = nama ? 'Halo ' + nama + ',' : 'Halo,';
  var greetEn = nama ? 'Hello ' + nama + ',' : 'Hello,';

  var subject = reminder
    ? 'Pengingat: laporan semester MMin Anda sudah tersedia (Reminder)'
    : 'Laporan semester MMin Anda sudah tersedia (Your report is ready)';

  var intro = reminder
    ? ['Jika Anda belum sempat membukanya, laporan semester MMin Anda (' + kelas + ', ' + semester + ') bisa dilihat di:',
       'If you have not had a chance to open it yet, your MMin semester report (' + kelas + ', ' + semester + ') is available at:']
    : ['Laporan semester MMin Anda (' + kelas + ', ' + semester + ') sudah bisa dilihat di:',
       'Your MMin semester report (' + kelas + ', ' + semester + ') is now available at:'];

  var body = [
    greetId, '', intro[0], url, '',
    'Cara membuka: masukkan email, kelas, dan nomor HP yang Anda daftarkan saat pendaftaran program, lalu klik "Lihat laporan".',
    'Jika ada kendala, silakan hubungi wali kelas Anda.',
    '',
    '-----',
    '',
    greetEn, '', intro[1], url, '',
    'To open it, enter the email, class, and phone number you used when registering for the program, then click "View report".',
    'If you run into any trouble, please contact your class advisor.',
    '',
    'APIIS — 21st Century Training. For Christians. For Free'
  ].join('\n');

  return { subject: subject, body: body };
}

function validNotifyJenis(jenis) {
  return jenis === 'baru' || jenis === 'pengingat';
}

/**
 * Admin: ringkasan untuk layar Notifikasi -- sisa kuota email, siapa yang
 * akan/tidak akan dikirimi untuk tiap jenis, isi email persis seperti yang
 * akan dikirim, dan riwayat pengiriman terakhir kelas ini.
 */
function adminNotifyStatus(kelas, force) {
  if (!kelas) return { ok: false, message: 'Kelas wajib diisi.' };
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var ctx = buildNotifyContext(ss, kelas);
  if (!ctx) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };

  var history = [];
  var notifSheet = ss.getSheetByName(NOTIF_LOG_SHEET);
  if (notifSheet) {
    history = readAccessLogSheet(notifSheet)
      .filter(function (r) { return r['Kelas'] === kelas; })
      .slice(-15)
      .reverse();
  }

  return {
    ok: true,
    sheetName: ctx.sheet.getName(),
    semester: ctx.semester,
    quota: MailApp.getRemainingDailyQuota(),
    ownerEmail: Session.getEffectiveUser().getEmail(),
    batchSize: NOTIF_BATCH_SIZE,
    totalStudents: ctx.students.length + ctx.invalid.length,
    invalidNames: ctx.invalid,
    plans: {
      baru: planNotification(ctx, 'baru', !!force),
      pengingat: planNotification(ctx, 'pengingat', !!force)
    },
    previews: {
      baru: renderEmail('baru', '(Nama Siswa)', kelas, ctx.semester),
      pengingat: renderEmail('pengingat', '(Nama Siswa)', kelas, ctx.semester)
    },
    history: history
  };
}

/**
 * Admin: kirim email `jenis` ke SATU batch (maks NOTIF_BATCH_SIZE) siswa yang
 * layak berikutnya, lalu kembalikan sisanya. Streamlit memanggil berulang
 * sampai `remaining` = 0. Setiap kiriman dicatat di _NotifLog (dipakai untuk
 * mencegah kirim ganda) dan ringkasannya di _AdminAuditLog.
 * `exclude` = email yang gagal pada putaran ini, supaya tidak dicoba terus.
 */
function adminNotifySend(kelas, jenis, admin, force, exclude) {
  if (!kelas) return { ok: false, message: 'Kelas wajib diisi.' };
  if (!validNotifyJenis(jenis)) return { ok: false, message: 'Jenis notifikasi tidak dikenal.' };
  var adminName = cleanAdminName(admin);

  return withScriptLock(function () {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var ctx = buildNotifyContext(ss, kelas);
    if (!ctx) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };

    var excluded = {};
    (exclude || []).forEach(function (e) { excluded[String(e).toLowerCase()] = true; });
    var queue = planNotification(ctx, jenis, !!force).eligible.filter(function (s) {
      return !excluded[s.email.toLowerCase()];
    });

    var quota = MailApp.getRemainingDailyQuota();
    if (queue.length > 0 && quota <= 0) {
      return { ok: false, code: 'quota', message: 'Kuota email harian habis.' };
    }

    var batch = queue.slice(0, Math.min(NOTIF_BATCH_SIZE, quota));
    var logRows = [];
    var sent = 0;
    var failed = [];
    batch.forEach(function (s) {
      var mail = renderEmail(jenis, s.nama, kelas, ctx.semester);
      try {
        MailApp.sendEmail({ to: s.email, subject: mail.subject, body: mail.body, name: MAIL_SENDER_NAME });
        sent++;
        logRows.push([new Date(), adminName, kelas, ctx.semester, safeCell(s.email), jenis, NOTIF_STATUS_SENT]);
      } catch (err) {
        failed.push(s.email);
        console.error('sendEmail gagal: ' + err);
        logRows.push([new Date(), adminName, kelas, ctx.semester, safeCell(s.email), jenis, 'gagal']);
      }
    });

    if (logRows.length) {
      appendLogRows(NOTIF_LOG_SHEET, NOTIF_LOG_HEADERS, logRows);
      appendLogRows(ADMIN_AUDIT_SHEET, ADMIN_AUDIT_HEADERS, [[
        new Date(), adminName, 'kirim_notifikasi', kelas, '', '', '', '',
        jenis + ': terkirim ' + sent + ', gagal ' + failed.length + (force ? ' (kirim ulang)' : '')
      ]]);
    }

    return {
      ok: true,
      sent: sent,
      failed: failed,
      remaining: queue.length - batch.length,
      quotaLeft: MailApp.getRemainingDailyQuota()
    };
  });
}

/** Admin: kirim satu email contoh ke pemilik script (akun yang men-deploy), bukan ke siswa. */
function adminNotifyTest(kelas, jenis, admin) {
  if (!kelas) return { ok: false, message: 'Kelas wajib diisi.' };
  if (!validNotifyJenis(jenis)) return { ok: false, message: 'Jenis notifikasi tidak dikenal.' };
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = findClassSheet(ss, kelas);
  if (!sheet) return { ok: false, message: 'Tab untuk kelas ini tidak ditemukan.' };
  var owner = Session.getEffectiveUser().getEmail();
  if (!owner) return { ok: false, message: 'Email pemilik script tidak terbaca.' };
  if (MailApp.getRemainingDailyQuota() <= 0) {
    return { ok: false, code: 'quota', message: 'Kuota email harian habis.' };
  }

  var mail = renderEmail(jenis, '(Nama Siswa)', kelas, displaySemesterLabel(sheet.getName(), kelas));
  MailApp.sendEmail({ to: owner, subject: '[TES] ' + mail.subject, body: mail.body, name: MAIL_SENDER_NAME });
  withScriptLock(function () {
    appendLogRows(ADMIN_AUDIT_SHEET, ADMIN_AUDIT_HEADERS, [[
      new Date(), cleanAdminName(admin), 'kirim_tes', kelas, '', '', '', '', jenis + ' -> ' + owner
    ]]);
  });
  return { ok: true, to: owner };
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
