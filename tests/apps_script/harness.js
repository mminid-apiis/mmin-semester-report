// Menjalankan Code.gs ASLI (google_apps_script/Code.gs) terhadap mock layanan Apps Script di memori.
// Tidak menyentuh Google Sheets/Gmail sungguhan dan tidak pernah mengirim email.
// Pakai:  node tests/apps_script/code_gs.test.js   (uji logika)
//         node tests/apps_script/mock_server.js    (backend palsu di http://127.0.0.1:8765 untuk uji UI;
//                                                   isi secrets lokal: apps_script_url = "http://127.0.0.1:8765",
//                                                   apps_script_secret = "test-shared-secret")
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');
const path = require('path');

const CODE_PATH = path.join(__dirname, '..', '..', 'google_apps_script', 'Code.gs');
const SECRET = 'test-shared-secret';

function isEmpty(v) { return v === '' || v === null || v === undefined; }

class Sheet {
  constructor(name) {
    this.name = name;
    this.grid = []; // grid[r][c]
    this.formats = {}; // "r,c" -> '@'
  }
  getName() { return this.name; }
  _ensure(r, c) {
    while (this.grid.length < r) this.grid.push([]);
    for (let i = 0; i < r; i++) while (this.grid[i].length < c) this.grid[i].push('');
  }
  getLastRow() {
    for (let r = this.grid.length - 1; r >= 0; r--) if (this.grid[r].some(v => !isEmpty(v))) return r + 1;
    return 0;
  }
  getLastColumn() {
    let max = 0;
    for (const row of this.grid) for (let c = row.length - 1; c >= 0; c--) if (!isEmpty(row[c])) { max = Math.max(max, c + 1); break; }
    return max;
  }
  getDataRange() { return this.getRange(1, 1, Math.max(this.getLastRow(), 1), Math.max(this.getLastColumn(), 1)); }
  getRange(r, c, nr, nc) { return new Range(this, r, c, nr || 1, nc || 1); }
  appendRow(arr) {
    const r = this.getLastRow() + 1;
    this.getRange(r, 1, 1, arr.length).setValues([arr]);
  }
}

class Range {
  constructor(sheet, r, c, nr, nc) { Object.assign(this, { sheet, r, c, nr, nc }); }
  getValues() {
    this.sheet._ensure(this.r + this.nr - 1, this.c + this.nc - 1);
    const out = [];
    for (let i = 0; i < this.nr; i++) {
      const row = [];
      for (let j = 0; j < this.nc; j++) {
        const v = this.sheet.grid[this.r - 1 + i][this.c - 1 + j];
        row.push(v instanceof Date ? new Date(v.getTime()) : v);
      }
      out.push(row);
    }
    return out;
  }
  setValues(vals) {
    if (vals.length !== this.nr || vals.some(row => row.length !== this.nc))
      throw new Error(`setValues dimension mismatch: range ${this.nr}x${this.nc} vs data ${vals.length}x${vals[0] && vals[0].length}`);
    this.sheet._ensure(this.r + this.nr - 1, this.c + this.nc - 1);
    for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) {
      let v = vals[i][j];
      const key = (this.r + i) + ',' + (this.c + j);
      if (typeof v === 'string') {
        if (v.startsWith("'")) v = v.slice(1); // apostrophe => literal text
        else if (this.sheet.formats[key] !== '@' && /^-?\d+(\.\d+)?$/.test(v.trim())) v = Number(v); // Sheets auto-parse
        else if (this.sheet.formats[key] !== '@' && v.startsWith('=')) v = '#FORMULA:' + v; // would become a formula
      }
      this.sheet.grid[this.r - 1 + i][this.c - 1 + j] = v;
    }
    return this;
  }
  clearContent() {
    this.sheet._ensure(this.r + this.nr - 1, this.c + this.nc - 1);
    for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) this.sheet.grid[this.r - 1 + i][this.c - 1 + j] = '';
    return this;
  }
  setNumberFormat(f) {
    for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) this.sheet.formats[(this.r + i) + ',' + (this.c + j)] = f;
    return this;
  }
}

function createWorld(opts = {}) {
  const world = {
    sheets: [],
    outbox: [],
    quota: opts.quota ?? 100,
    failEmails: new Set(),
    lockHeld: 0,
    lockMaxHeld: 0,
    lockAcquired: 0,
    owner: 'owner@example.test',
    now: null, // override Date for time travel if needed
  };
  const ss = {
    getSheets: () => world.sheets,
    getSheetByName: n => world.sheets.find(s => s.name === n) || null,
    getNumSheets: () => world.sheets.length,
    insertSheet(name, idx) {
      const s = new Sheet(name);
      if (idx === undefined) world.sheets.unshift(s); else world.sheets.splice(idx, 0, s);
      return s;
    },
  };
  world.ss = ss;
  world.addSheet = (name, headers, rows, textCols = []) => {
    const s = ss.insertSheet(name, world.sheets.length);
    s.getRange(1, 1, 1, headers.length).setValues([headers]);
    textCols.forEach(ci => { for (let r = 2; r <= rows.length + 1; r++) s.formats[r + ',' + (ci + 1)] = '@'; });
    if (rows.length) s.getRange(2, 1, rows.length, headers.length).setValues(rows);
    return s;
  };

  const context = {
    console: { log() {}, error: (...a) => { world.errors = (world.errors || []).concat(a.join(' ')); } },
    SpreadsheetApp: { openById: () => ss, flush() {} },
    ContentService: {
      MimeType: { JSON: 'json' },
      createTextOutput: s => ({ _s: s, setMimeType() { return this; }, getContent() { return this._s; } }),
    },
    Utilities: {
      DigestAlgorithm: { MD5: 'MD5' },
      Charset: { UTF_8: 'UTF_8' },
      computeDigest(alg, str) {
        const buf = crypto.createHash('md5').update(str, 'utf8').digest();
        return Array.from(new Int8Array(buf)); // Apps Script returns SIGNED bytes
      },
      formatDate(d, tz, fmt) {
        const parts = new Intl.DateTimeFormat('en-CA', {
          timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
        }).formatToParts(d).reduce((a, p) => (a[p.type] = p.value, a), {});
        return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
      },
    },
    LockService: {
      getScriptLock: () => ({
        waitLock() { world.lockHeld++; world.lockAcquired++; world.lockMaxHeld = Math.max(world.lockMaxHeld, world.lockHeld); },
        releaseLock() { world.lockHeld--; },
      }),
    },
    MailApp: {
      getRemainingDailyQuota: () => world.quota,
      sendEmail(m) {
        if (world.failEmails.has(String(m.to).toLowerCase())) throw new Error('simulated failure for ' + m.to);
        if (world.quota <= 0) throw new Error('quota exhausted');
        world.quota--;
        world.outbox.push({ to: m.to, subject: m.subject, body: m.body, name: m.name });
      },
    },
    Session: { getEffectiveUser: () => ({ getEmail: () => world.owner }) },
  };
  vm.createContext(context);
  let src = fs.readFileSync(CODE_PATH, 'utf8')
    .replace("'GANTI_DENGAN_SPREADSHEET_ID'", "'test-ss'")
    .replace("'GANTI_DENGAN_SHARED_SECRET'", `'${SECRET}'`);
  vm.runInContext(src, context);
  world.ctx = context;
  world.call = (action, payload = {}) => {
    const out = context.doPost({ postData: { contents: JSON.stringify({ action, secret: SECRET, ...payload }) } });
    return JSON.parse(out.getContent());
  };
  return world;
}

const HEADERS = ['Email', 'Nomor HP', 'Nama', 'Kelas', 'Total Persentase Kuis', 'Total Persentase Kehadiran', 'Catatan'];

function seedWorld(world) {
  world.addSheet('Semester 1 Leadership', HEADERS, [
    ['lama@example.com', '081200000000', 'Siswa Lama', 'MMin 2 Leadership', 50, 50, ''],
  ], [1]);
  world.addSheet('Semester 2 Leadership', HEADERS, [
    ['testsatu@example.com', '081234500001', 'Test Satu', 'MMin 2 Leadership', 88, 95, 'Baik.'],
    ['testdua@example.com', '081234500002', 'Test Dua', 'MMin 2 Leadership', 82, 68, ''],
    ['testlima@example.com', '081234500005', 'Test Lima', 'MMin 2 Leadership', 90, 91, ''],
    ['', '081234500099', 'Tanpa Email', 'MMin 2 Leadership', 70, 70, ''],
    ['bukan-email', '081234500098', 'Email Rusak', 'MMin 2 Leadership', 70, 70, ''],
  ], [1]);
  // Pastoral punya dua kolom opsional ("Minggu Tercatat", "Total Minggu") untuk menguji
  // bahwa kolom tambahan ikut terbaca/tersimpan dan tidak merusak audit diff.
  world.addSheet('Semester 2 Pastoral', [...HEADERS, 'Minggu Tercatat', 'Total Minggu'], [
    ['testtiga@example.com', '081234500003', 'Test Tiga', 'MMin 2 Pastoral', 65, 90, '', 16, 16],
  ], [1]);
  return world;
}

module.exports = { createWorld, seedWorld, HEADERS, SECRET };
