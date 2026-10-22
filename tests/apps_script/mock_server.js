// Backend palsu berbasis Code.gs asli (layanan Apps Script di-mock). Tidak pernah mengirim email sungguhan.
// Endpoint debug: /_debug/outbox, /_debug/sheet?name=, /_debug/quota?set=, /_debug/reset, /_debug/fail?email=, /_debug/locks
const http = require('http');
const url = require('url');
const { createWorld, seedWorld, SECRET } = require('./harness');

let world = seedWorld(createWorld());

function readBody(req) {
  return new Promise(resolve => { let b = ''; req.on('data', c => b += c); req.on('end', () => resolve(b)); });
}

http.createServer(async (req, res) => {
  const u = url.parse(req.url, true);
  const send = (obj, code = 200) => { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); };

  if (u.pathname === '/_debug/outbox') return send(world.outbox);
  if (u.pathname === '/_debug/sheet') {
    const s = world.ss.getSheetByName(u.query.name);
    return send(s ? s.getDataRange().getValues() : null);
  }
  if (u.pathname === '/_debug/quota') { world.quota = Number(u.query.set); return send({ quota: world.quota }); }
  if (u.pathname === '/_debug/reset') { world = seedWorld(createWorld()); return send({ reset: true }); }
  if (u.pathname === '/_debug/fail') { world.failEmails.add(String(u.query.email).toLowerCase()); return send({ ok: true }); }
  if (u.pathname === '/_debug/locks') return send({ held: world.lockHeld, acquired: world.lockAcquired });

  if (req.method !== 'POST') return send({ ok: true, message: 'mock gas up' });
  const body = await readBody(req);
  const out = world.ctx.doPost({ postData: { contents: body } });
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(out.getContent());
}).listen(8765, '127.0.0.1', () => console.log('GAS mock listening on 8765, secret=' + SECRET));
