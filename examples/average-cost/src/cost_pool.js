// Production logic: running average cost per item and location.
// This is the code under review. The Python rebuild in tieout/ must not be
// translated from it.
function buildLedger(events) {
  const pools = {};
  const sorted = events.slice().sort((a, b) => a.created.localeCompare(b.created));
  for (const e of sorted) {
    const k = e.item + '|' + e.location;
    const p = pools[k] || (pools[k] = { qty: 0, value: 0 });
    const q = Number(e.quantity);
    if (q === 0) continue;
    const avg = p.qty > 0 ? p.value / p.qty : 0;
    const inbound = q > 0 && e.type !== 'RtnAuth';
    const dv = inbound ? Number(e.amount) : Math.round(q * avg * 100) / 100;
    p.qty += q;
    p.value += dv;
    if (p.qty === 0) p.value = 0;
  }
  return pools;
}

if (require.main === module) {
  const fs = require('fs');
  const [head, ...rows] = fs.readFileSync(process.argv[2], 'utf8').trim().split('\n');
  const cols = head.split(',');
  const events = rows.map(r => Object.fromEntries(r.split(',').map((v, i) => [cols[i], v])));
  const out = {};
  for (const [k, p] of Object.entries(buildLedger(events))) {
    out[k] = { qty: p.qty, value: Math.round(p.value * 100) / 100 };
  }
  process.stdout.write(JSON.stringify(out, null, 2) + '\n');
}

module.exports = { buildLedger };
