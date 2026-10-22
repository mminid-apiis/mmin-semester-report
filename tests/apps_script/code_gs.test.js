const { createWorld, seedWorld, HEADERS } = require('./harness');

let pass = 0, fail = 0;
function ok(cond, msg) { if (cond) { pass++; } else { fail++; console.log('  FAIL:', msg); } }
function eq(a, b, msg) { ok(JSON.stringify(a) === JSON.stringify(b), `${msg} — expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`); }
function section(n) { console.log('\n# ' + n); }

function fresh(opts) { const w = seedWorld(createWorld(opts)); return w; }
function auditRows(w) { const r = w.call('admin_audit_log'); ok(r.ok, 'audit_log ok'); return r.rows; }
function cols(rows, c) { return rows.map(r => r[c]); }

section('existing behaviour still intact');
{
  const w = fresh();
  eq(w.call('ping').message, 'pong', 'ping');
  eq(w.call('list_semesters').semesters, ['Semester 1 Leadership', 'Semester 2 Leadership', 'Semester 2 Pastoral'], 'list_semesters hides _ tabs');
  const r = w.call('get_report', { kelas: 'MMin 2 Leadership', phone: '+62 812-3450-0001', email: 'TestSatu@Example.com' });
  ok(r.ok && r.semester === 'Semester 2' && r.data.Nama === 'Test Satu', 'get_report matches, uses rightmost tab');
  ok(!w.call('get_report', { kelas: 'MMin 2 Leadership', phone: '0000', email: 'testsatu@example.com' }).ok, 'wrong phone rejected');
  const log = w.call('admin_access_log').rows;
  eq(log.length, 1, 'one access logged');
  eq(log[0].Semester, 'Semester 2', 'access log semester');
  ok(!w.call('list_semesters').semesters.some(n => n.startsWith('_')), 'log tabs hidden from list_semesters');
  eq(w.call('bogus').message, 'Action tidak dikenal.', 'unknown action');
  eq(createWorld().ctx.doPost({ postData: { contents: JSON.stringify({ action: 'ping', secret: 'x' }) } }).getContent(), '{"ok":false,"message":"Unauthorized."}', 'bad secret');
}

section('admin_log_event');
{
  const w = fresh();
  ok(w.call('admin_log_event', { admin: 'admin1', event: 'login' }).ok, 'login logged');
  ok(w.call('admin_log_event', { admin: 'admin2', event: 'login_gagal', detail: 'password salah' }).ok, 'failed login logged');
  ok(w.call('admin_log_event', { admin: 'admin1', event: 'logout' }).ok, 'logout logged');
  ok(!w.call('admin_log_event', { admin: 'admin1', event: 'simpan_nilai' }).ok, 'arbitrary event rejected');
  ok(!w.call('admin_log_event', { admin: 'admin1', event: 'ubah_nilai' }).ok, 'cannot forge audit actions');
  w.call('admin_log_event', { admin: '=HYPERLINK("http://evil")', event: 'login', detail: '=1+1' });
  w.call('admin_log_event', { admin: '   ', event: 'login' });
  w.call('admin_log_event', { admin: 'x'.repeat(100), event: 'login' });
  const rows = auditRows(w);
  eq(cols(rows, 'Aksi').slice(0, 3), ['login', 'login_gagal', 'logout'], 'actions recorded in order');
  eq(cols(rows, 'Admin').slice(0, 3), ['admin1', 'admin2', 'admin1'], 'admin names recorded');
  ok(/^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$/.test(rows[0].Timestamp), 'timestamp formatted WIB string');
  ok(!JSON.stringify(rows).includes('#FORMULA'), 'formula injection neutralised');
  eq(rows[3].Admin, '=HYPERLINK("http://evil")', 'text kept literal after apostrophe stripping');
  eq(rows[4].Admin, '(tidak diketahui)', 'blank admin name');
  eq(rows[5].Admin.length, 40, 'admin name capped at 40');
  eq(w.lockHeld, 0, 'lock released');
}

section('admin_list_class + admin_save_class: audit diff');
{
  const w = fresh();
  const l1 = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  ok(l1.ok && l1.version && l1.rows.length === 5 && l1.sheetName === 'Semester 2 Leadership', 'list ok');
  const l1b = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  eq(l1b.version, l1.version, 'version stable across reads');

  // 1) save unchanged, but as strings the way Streamlit/CSV would send them
  const asStrings = l1.rows.map(r => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, String(v)])));
  let s = w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: asStrings, admin: 'admin1', baseVersion: l1.version });
  ok(s.ok, 'unchanged save ok');
  eq(s.changes, { ubah: 0, tambah: 0, hapus: 0 }, 'numeric-vs-string is NOT a change');
  eq(s.version, l1.version, 'version unchanged after no-op save');
  let rows = auditRows(w);
  eq(rows.length, 1, 'only summary row');
  ok(rows[0].Aksi === 'simpan_nilai' && rows[0].Keterangan.startsWith('Tanpa perubahan'), 'no-change summary');

  // 2) real edits: grade change, phone change (masked), add, delete
  const edited = JSON.parse(JSON.stringify(l1.rows));
  edited[1]['Total Persentase Kehadiran'] = 80;          // Test Dua 68 -> 80
  edited[0]['Nomor HP'] = '081299999999';                 // phone changed
  edited.splice(2, 1);                                    // delete Test Lima
  edited.push({ Email: 'baru@example.com', 'Nomor HP': '081211112222', Nama: 'Siswa Baru', Kelas: 'MMin 2 Leadership', 'Total Persentase Kuis': 77, 'Total Persentase Kehadiran': 88, Catatan: '' });
  s = w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: edited, admin: 'admin2', baseVersion: s.version });
  ok(s.ok, 'edit save ok');
  eq(s.changes, { ubah: 2, tambah: 1, hapus: 1 }, 'change counts');
  rows = auditRows(w).slice(1);
  const byAksi = a => rows.filter(r => r.Aksi === a);
  eq(byAksi('simpan_nilai').length, 1, 'one summary');
  ok(byAksi('simpan_nilai')[0].Keterangan.includes('Ubah 2 sel, tambah 1 siswa, hapus 1 siswa'), 'summary text: ' + byAksi('simpan_nilai')[0].Keterangan);
  const grade = byAksi('ubah_nilai').find(r => r.Kolom === 'Total Persentase Kehadiran');
  ok(grade && grade['Siswa (Email)'] === 'testdua@example.com' && String(grade['Nilai Lama']) === '68' && String(grade['Nilai Baru']) === '80' && grade.Admin === 'admin2', 'grade change recorded with who/old/new');
  const phone = byAksi('ubah_nilai').find(r => r.Kolom === 'Nomor HP');
  ok(phone && phone['Nilai Lama'] === '(disembunyikan)' && phone['Nilai Baru'] === '(disembunyikan)', 'phone masked');
  ok(!JSON.stringify(rows).includes('081299999999') && !JSON.stringify(rows).includes('081234500001'), 'no phone number leaks into audit log');
  eq(byAksi('tambah_siswa')[0]['Siswa (Email)'], 'baru@example.com', 'added student');
  eq(byAksi('hapus_siswa')[0]['Siswa (Email)'], 'testlima@example.com', 'deleted student');
  eq(byAksi('hapus_siswa')[0].Keterangan, 'Test Lima', 'deleted student name kept');

  // phone kept as text with leading zero
  const l2 = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  eq(l2.version, s.version, 'returned version == fresh list version');
  eq(l2.rows.find(r => r.Email === 'baru@example.com')['Nomor HP'], '081211112222', 'leading zero preserved');
  eq(l2.rows.length, 5, 'row count after edits (5 -1 +1)');

  // 3) empty save wipes rows and is logged
  const w2 = fresh();
  const base = w2.call('admin_list_class', { kelas: 'MMin 2 Pastoral' });
  const e = w2.call('admin_save_class', { kelas: 'MMin 2 Pastoral', rows: [], admin: 'admin3', baseVersion: base.version });
  ok(e.ok && e.savedRows === 0 && e.changes.hapus === 1, 'empty save removes all and counts deletes');
  eq(w2.call('admin_list_class', { kelas: 'MMin 2 Pastoral' }).rows.length, 0, 'sheet emptied');
  eq(w.lockHeld + w2.lockHeld, 0, 'locks released');
}

section('concurrent admins: optimistic locking');
{
  const w = fresh();
  const loadedByA = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  const loadedByB = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  const a = JSON.parse(JSON.stringify(loadedByA.rows)); a[0]['Total Persentase Kuis'] = 99;
  const sa = w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: a, admin: 'admin1', baseVersion: loadedByA.version });
  ok(sa.ok, 'A saves first');
  const b = JSON.parse(JSON.stringify(loadedByB.rows)); b[1]['Catatan'] = 'dari B';
  const sb = w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: b, admin: 'admin2', baseVersion: loadedByB.version });
  ok(!sb.ok && sb.code === 'conflict', 'B is rejected with code=conflict');
  const now = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  eq(now.rows[0]['Total Persentase Kuis'], 99, "A's edit survived");
  ok(now.rows[1].Catatan !== 'dari B', "B's edit NOT applied");
  const rows = auditRows(w);
  ok(rows.some(r => r.Aksi === 'simpan_ditolak' && r.Admin === 'admin2'), 'rejection audited');
  // B reloads then saves fine
  const reload = w.call('admin_list_class', { kelas: 'MMin 2 Leadership' });
  const b2 = JSON.parse(JSON.stringify(reload.rows)); b2[1].Catatan = 'dari B';
  ok(w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: b2, admin: 'admin2', baseVersion: reload.version }).ok, 'B succeeds after reload');
  // legacy client without baseVersion still works
  ok(w.call('admin_save_class', { kelas: 'MMin 2 Leadership', rows: b2 }).ok, 'legacy save (no baseVersion/admin) still works');
  ok(auditRows(w).some(r => r.Admin === '(tidak diketahui)' && r.Aksi === 'simpan_nilai'), 'legacy save audited as unknown admin');
  eq(w.lockHeld, 0, 'locks released after conflict path');
  ok(w.lockMaxHeld === 1, 'never nested locks');
}

section('notify: status + previews');
{
  const w = fresh();
  const s = w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' });
  ok(s.ok, 'status ok');
  eq(s.semester, 'Semester 2', 'semester label');
  eq(s.quota, 100, 'quota reported');
  eq(s.ownerEmail, 'owner@example.test', 'owner email reported');
  eq(s.plans.baru.eligible.map(x => x.email), ['testsatu@example.com', 'testdua@example.com', 'testlima@example.com'], 'eligible = valid emails only');
  eq(s.invalidNames.sort(), ['Email Rusak', 'Tanpa Email'], 'invalid-email students listed by name');
  eq(s.totalStudents, 5, 'total includes invalid');
  for (const j of ['baru', 'pengingat']) {
    const body = s.previews[j].subject + '\n' + s.previews[j].body;
    ok(body.includes('https://mmin-semester-report.streamlit.app/'), j + ' has portal link');
    ok(!/75|70%|lulus|pass|及格|kuis|quiz|nilai|grade|persen/i.test(body.replace(/Lihat laporan|View report/g, '')), j + ' leaks no grades/thresholds: ' + (body.match(/75|70%|lulus|pass|及格|kuis|quiz|nilai|grade|persen/i) || [''])[0]);
    ok(body.includes('(Nama Siswa)') && body.includes('Halo') && body.includes('Hello') && body.includes('您好'), j + ' trilingual + greeting');
  }
  ok(s.previews.pengingat.subject.startsWith('Pengingat'), 'reminder subject');
  ok(!w.call('admin_notify_status', { kelas: 'MMin 9 Nope' }).ok, 'unknown class');
  eq(w.outbox.length, 0, 'status sends nothing');
}

section('notify: send batches, dedupe, force');
{
  const w = fresh();
  // grow Leadership roster to 70 valid students
  const sh = w.ss.getSheetByName('Semester 2 Leadership');
  const extra = [];
  for (let i = 0; i < 67; i++) extra.push([`mass${i}@example.com`, `0812000${String(i).padStart(5, '0')}`, `Mass ${i}`, 'MMin 2 Leadership', 80, 80, '']);
  sh.getRange(7, 1, extra.length, HEADERS.length).setValues(extra);
  const total = w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' }).plans.baru.eligible.length;
  eq(total, 70, '70 eligible');

  let loops = 0, sent = 0, remaining = null;
  while (true) {
    const r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
    ok(r.ok, 'send batch ok');
    ok(r.sent <= 30, 'batch <= 30');
    sent += r.sent; remaining = r.remaining; loops++;
    if (remaining === 0 || loops > 10) break;
  }
  eq([sent, loops], [70, 3], '70 sent over 3 batches');
  eq(w.outbox.length, 70, 'outbox has 70');
  eq(new Set(w.outbox.map(m => m.to)).size, 70, 'no duplicate recipients');
  ok(w.outbox.every(m => !['bukan-email', ''].includes(m.to)), 'never sends to invalid addresses');
  ok(!w.outbox.some(m => m.to === 'testtiga@example.com'), 'never sends to other class');
  ok(w.outbox.every(m => !m.subject.startsWith('[TES]')), 'real mails are not marked test');
  ok(w.outbox[0].body.includes('Halo Test Satu,'), 'personalised greeting');
  eq(w.quota, 30, 'quota consumed');

  const again = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
  eq([again.ok, again.sent, again.remaining], [true, 0, 0], 'second run sends nothing (already sent)');
  const st = w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' });
  eq(st.plans.baru.eligible.length, 0, 'status shows 0 eligible');
  ok(st.plans.baru.skipped.every(x => x.reason === 'sudah_dikirim') && st.plans.baru.skipped.length === 70, 'skipped reason sudah_dikirim');
  eq(st.history.length, 15, 'history capped to 15');
  ok(st.history[0].Status === 'terkirim' && st.history[0].Jenis === 'baru', 'history rows shaped');

  const forced = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin2', force: true });
  eq(forced.sent, 30, 'force resends (one batch)');
  const aud = auditRows(w).filter(r => r.Aksi === 'kirim_notifikasi');
  eq(aud.length, 4, 'one audit row per non-empty batch (3 + 1 forced)');
  ok(aud[3].Keterangan.includes('(kirim ulang)') && aud[3].Admin === 'admin2', 'forced batch audited');
  eq(w.lockHeld, 0, 'locks released');
}

section('notify: failures, exclude, quota');
{
  const w = fresh();
  w.failEmails.add('testdua@example.com');
  let r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
  eq([r.sent, r.failed], [2, ['testdua@example.com']], 'failure reported, others sent');
  const st1 = w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' });
  eq(st1.plans.baru.eligible.map(x => x.email), ['testdua@example.com'], 'failed student stays eligible (retry later)');
  r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1', exclude: ['testdua@example.com'] });
  eq([r.sent, r.remaining], [0, 0], 'exclude prevents infinite retry loop');
  w.failEmails.clear();
  r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
  eq(r.sent, 1, 'retry succeeds later');
  ok(w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' }).history.some(h => h.Status === 'gagal'), 'failure logged in history');

  const q = fresh({ quota: 2 });
  r = q.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
  eq([r.sent, r.remaining, r.quotaLeft], [2, 1, 0], 'quota caps the batch, remainder reported');
  r = q.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin1' });
  ok(!r.ok && r.code === 'quota', 'quota exhausted -> code=quota');
  const none = fresh({ quota: 0 });
  none.call('get_report', { kelas: 'MMin 2 Pastoral', phone: '081234500003', email: 'testtiga@example.com' }); // only Pastoral student has opened -> nobody to remind
  r = none.call('admin_notify_send', { kelas: 'MMin 2 Pastoral', jenis: 'pengingat', admin: 'a' });
  ok(r.ok && r.sent === 0, 'nothing eligible + zero quota is not an error');
  ok(!none.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'hack', admin: 'a' }).ok, 'bad jenis rejected');
}

section('notify: reminders');
{
  const w = fresh();
  // testsatu opens the report this semester; testdua opened only in an OLD semester
  w.call('get_report', { kelas: 'MMin 2 Leadership', phone: '081234500001', email: 'testsatu@example.com' });
  const logSheet = w.ss.getSheetByName('_AccessLog_Leadership');
  logSheet.appendRow([new Date(), 'Test Dua', 'testdua@example.com', 'MMin 2 Leadership', 'Semester 1']);
  const st = w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' });
  eq(st.plans.pengingat.eligible.map(x => x.email).sort(), ['testdua@example.com', 'testlima@example.com'], 'reminder skips only this-semester openers');
  eq(st.plans.pengingat.skipped, [{ nama: 'Test Satu', email: 'testsatu@example.com', reason: 'sudah_membuka' }], 'skip reason sudah_membuka');
  let r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'pengingat', admin: 'admin1' });
  eq(r.sent, 2, 'reminded 2');
  ok(w.outbox.every(m => m.subject.startsWith('Pengingat')), 'reminder subject used');
  ok(!w.outbox.some(m => m.to === 'testsatu@example.com'), 'opener not reminded');
  r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'pengingat', admin: 'admin1' });
  eq(r.sent, 0, 'cooldown blocks immediate re-reminder');
  eq(w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' }).plans.pengingat.skipped.filter(x => x.reason === 'baru_diingatkan').length, 2, 'reason baru_diingatkan');
  r = w.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'pengingat', admin: 'admin1', force: true });
  eq(r.sent, 2, 'force overrides cooldown');
  const w2 = fresh();
  w2.call('get_report', { kelas: 'MMin 2 Leadership', phone: '081234500001', email: 'testsatu@example.com' });
  r = w2.call('admin_notify_send', { kelas: 'MMin 2 Leadership', jenis: 'pengingat', admin: 'a', force: true });
  ok(!w2.outbox.some(m => m.to === 'testsatu@example.com'), 'force never reminds someone who already opened');
  // "baru" and "pengingat" are tracked independently
  const w3 = fresh();
  w3.call('admin_notify_send', { kelas: 'MMin 2 Pastoral', jenis: 'baru', admin: 'a' });
  eq(w3.call('admin_notify_status', { kelas: 'MMin 2 Pastoral' }).plans.pengingat.eligible.length, 1, 'sending baru does not block pengingat');
}

section('notify: test mail goes to owner only');
{
  const w = fresh();
  const r = w.call('admin_notify_test', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'admin3' });
  eq([r.ok, r.to], [true, 'owner@example.test'], 'test ok');
  eq(w.outbox.length, 1, 'exactly one mail');
  ok(w.outbox[0].to === 'owner@example.test' && w.outbox[0].subject.startsWith('[TES] '), 'to owner, marked [TES]');
  ok(!w.ss.getSheetByName('_NotifLog'), 'test mail is not recorded as a student notification');
  ok(auditRows(w).some(x => x.Aksi === 'kirim_tes' && x.Admin === 'admin3'), 'test audited');
  eq(w.call('admin_notify_status', { kelas: 'MMin 2 Leadership' }).plans.baru.eligible.length, 3, 'test does not affect eligibility');
  const z = fresh({ quota: 0 });
  ok(z.call('admin_notify_test', { kelas: 'MMin 2 Leadership', jenis: 'baru', admin: 'a' }).code === 'quota', 'test respects quota');
}

section('log tabs are invisible to the student side');
{
  const w = fresh();
  w.call('admin_log_event', { admin: 'a', event: 'login' });
  w.call('admin_notify_send', { kelas: 'MMin 2 Pastoral', jenis: 'baru', admin: 'a' });
  const names = w.call('list_semesters').semesters;
  ok(!names.includes('_AdminAuditLog') && !names.includes('_NotifLog'), 'hidden from list_semesters');
  const lead = w.call('get_report', { kelas: 'MMin 2 Leadership', phone: '081234500001', email: 'testsatu@example.com' });
  ok(lead.ok && lead.semester === 'Semester 2', 'findClassSheet unaffected by new _ tabs');
  ok(w.call('admin_access_log').rows.every(r => 'Semester' in r), 'admin_access_log unaffected by new tabs');
  ok(w.ss.getSheets().slice(-2).every(s => s.name.startsWith('_')), 'new log tabs created at the end');
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
