import { meshCentroid, primaryMeshesInBBox, circleBBox, aggregateCircle } from "./mesh.js";
import { INDUSTRIES, DEFAULTS, plan, fmtYen, fmtRange } from "./calc.js";

// S4計器: 配布計画レポートの事前登録フォーム(裏のサービスは未実装＝需要温度計)
const FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkgvgKGaOWWRiwzZcz3_GW1XH_SRMBPvOQjVRQeuAeFKUqw/viewform";

const map = L.map("map", { zoomControl: true }).setView([35.6895, 139.6917], 14);
L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noopener">地理院タイル</a>',
}).addTo(map);

const els = {
  radius: document.getElementById("radius"),
  radiusOut: document.getElementById("radiusOut"),
  status: document.getElementById("status"),
  results: document.getElementById("results"),
  deliverable: document.getElementById("deliverable"),
  copies: document.getElementById("copies"),
  costTotal: document.getElementById("costTotal"),
  responses: document.getElementById("responses"),
  breakdown: document.getElementById("breakdown"),
  cpa: document.getElementById("cpa"),
  industry: document.getElementById("industry"),
  coverage: document.getElementById("coverage"),
  spare: document.getElementById("spare"),
  unitPrint: document.getElementById("unitPrint"),
  unitDeliver: document.getElementById("unitDeliver"),
  rateNote: document.getElementById("rateNote"),
  maskNote: document.getElementById("maskNote"),
  shareMeta: document.getElementById("shareMeta"),
  ctaLink: document.getElementById("ctaLink"),
  addr: document.getElementById("addr"),
  addrList: document.getElementById("addrList"),
};

els.ctaLink.href = FORM_URL;

for (const ind of INDUSTRIES) {
  const o = document.createElement("option");
  o.value = ind.id;
  o.textContent = `${ind.label}（${fmtRange(ind.lo, ind.hi, 2)}%）`;
  els.industry.append(o);
}
els.industry.value = "food";
els.coverage.value = DEFAULTS.coverage;
els.spare.value = DEFAULTS.spare;
els.unitPrint.value = DEFAULTS.unitPrint;
els.unitDeliver.value = DEFAULTS.unitDeliver;

const fmt = (n) => Math.round(n).toLocaleString("ja-JP");

// ---- メッシュ読み込み ----
let manifest = null;
const meshCache = new Map();

async function loadMesh(code1) {
  if (meshCache.has(code1)) return meshCache.get(code1);
  const p = (async () => {
    if (manifest && !manifest.meshes.includes(code1)) return "missing";
    try {
      const rows = await (await fetch(`data/${code1}.json`)).json();
      return {
        cells: rows.map(([mc, pop, hh]) => {
          const [la, lo] = meshCentroid(mc);
          return { la, lo, pop, hh };
        }),
      };
    } catch {
      return "missing";
    }
  })();
  meshCache.set(code1, p);
  const v = await p;
  meshCache.set(code1, v);
  return v;
}

async function aggregateAt(c, r) {
  const [latMin, latMax, lonMin, lonMax] = circleBBox(c.lat, c.lng, r);
  const codes = primaryMeshesInBBox(latMin, latMax, lonMin, lonMax);
  const loaded = await Promise.all(codes.map(loadMesh));
  const cells = loaded.filter((m) => m !== "missing").flatMap((m) => m.cells);
  const missing = codes.filter((_, i) => loaded[i] === "missing");
  return { agg: aggregateCircle(cells, c.lat, c.lng, r), missing };
}

// ---- 状態 ----
let center = null;
let circle = null;

function radius() {
  return +els.radius.value;
}

function params() {
  const ind = INDUSTRIES.find((i) => i.id === els.industry.value) ?? INDUSTRIES[0];
  return {
    coverage: clamp(+els.coverage.value, 10, 100),
    spare: clamp(+els.spare.value, 0, 30),
    unitPrint: clamp(+els.unitPrint.value, 0, 100),
    unitDeliver: clamp(+els.unitDeliver.value, 0, 100),
    industry: ind,
  };
}

function clamp(v, lo, hi) {
  return Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : lo;
}

function setCenter(latlng, opts = {}) {
  center = latlng;
  if (!circle) {
    circle = L.circle(latlng, { radius: radius(), color: "#2a78d6", weight: 2, fillOpacity: 0.08 }).addTo(map);
  } else {
    circle.setLatLng(latlng).setRadius(radius());
  }
  if (opts.pan) map.setView(latlng, opts.zoom ?? map.getZoom());
  recompute();
}

map.on("click", (e) => setCenter(e.latlng));

els.radius.addEventListener("input", () => {
  els.radiusOut.textContent = `${(radius() / 1000).toFixed(1)} km`;
  if (circle) circle.setRadius(radius());
  recompute();
});

for (const el of [els.industry, els.coverage, els.spare, els.unitPrint, els.unitDeliver]) {
  el.addEventListener("input", () => recompute());
}

let seq = 0;
async function recompute() {
  if (!center) return;
  const my = ++seq;
  els.status.textContent = "集計中…";
  const r = radius();
  const { agg, missing } = await aggregateAt(center, r);
  if (my !== seq) return;

  const p = params();
  const res = plan({
    households: agg.hh,
    coverage: p.coverage,
    spare: p.spare,
    unitPrint: p.unitPrint,
    unitDeliver: p.unitDeliver,
    rateLo: p.industry.lo,
    rateHi: p.industry.hi,
  });

  els.status.hidden = true;
  els.results.hidden = false;
  els.deliverable.textContent = `${fmt(res.deliverable)} 部`;
  els.copies.textContent = `${fmt(res.copies)} 部`;
  els.costTotal.textContent = fmtYen(res.costTotal);
  els.responses.textContent = res.responsesHi >= 1
    ? `${fmtRange(res.responsesLo, res.responsesHi, res.responsesHi < 10 ? 1 : 0)} 件`
    : `1件未満`;

  els.breakdown.textContent =
    `圏内世帯数 ${fmt(agg.hh)}（人口 ${fmt(agg.pop)}）／ 印刷 ${fmtYen(res.costPrint)}＋配布 ${fmtYen(res.costDeliver)}`;
  els.cpa.textContent = res.cpaLo
    ? `1件あたり獲得コスト ${fmtYen(res.cpaLo)}〜${fmtYen(res.cpaHi)}（反響率 ${fmtRange(p.industry.lo, p.industry.hi, 2)}% で計算）`
    : "反響率の想定が0のため獲得コストは計算できません";

  els.rateNote.textContent =
    `反響率は業界公表値の目安です（出典: 記事内に明記）。${p.industry.note ?? ""}` +
    ` 実際の反響は紙面・時期・競合で大きく動きます。`;

  const masked = agg.maskedCells > 0;
  els.maskNote.hidden = !masked;
  if (masked) els.maskNote.textContent = `秘匿処理で世帯数が空のセルが ${agg.maskedCells} 件あります（その分だけ過小評価になります）。`;
  if (missing.length) {
    els.maskNote.hidden = false;
    els.maskNote.textContent += ` 圏内にデータ範囲外の区画があります。`;
  }

  syncUrl();
}

function syncUrl() {
  if (!center) return;
  const p = params();
  const q = new URLSearchParams({
    lat: center.lat.toFixed(5),
    lng: center.lng.toFixed(5),
    r: String(radius()),
    ind: p.industry.id,
    cov: String(p.coverage),
    sp: String(p.spare),
    up: String(p.unitPrint),
    ud: String(p.unitDeliver),
  });
  const url = `${location.pathname}?${q}`;
  history.replaceState(null, "", url);
  els.shareMeta.textContent = "この計算結果はURLで共有できます。";
}

function applyUrlState() {
  const q = new URLSearchParams(location.search);
  const lat = parseFloat(q.get("lat"));
  const lng = parseFloat(q.get("lng"));
  const r = parseInt(q.get("r") ?? "", 10);
  if (q.get("ind") && INDUSTRIES.some((i) => i.id === q.get("ind"))) els.industry.value = q.get("ind");
  for (const [key, el] of [["cov", els.coverage], ["sp", els.spare], ["up", els.unitPrint], ["ud", els.unitDeliver]]) {
    const v = parseFloat(q.get(key) ?? "");
    if (Number.isFinite(v)) el.value = String(v);
  }
  if (Number.isFinite(r)) {
    els.radius.value = String(r);
    els.radiusOut.textContent = `${(r / 1000).toFixed(1)} km`;
  }
  if (Number.isFinite(lat) && Number.isFinite(lng)) {
    setCenter(L.latLng(lat, lng), { pan: true, zoom: 15 });
  }
}

fetch("data/manifest.json")
  .then((r) => r.json())
  .then((m) => { manifest = m; applyUrlState(); })
  .catch(() => { els.status.textContent = "manifest.json を読めません。build_slim_data.py を実行してください"; });

// ---- 住所検索(地理院) ----
let addrSeq = 0;
els.addr.addEventListener("input", () => {
  const q = els.addr.value.trim();
  if (q.length < 2) { els.addrList.hidden = true; return; }
  searchAddress(q);
});
document.addEventListener("click", (e) => {
  if (!els.addrList.contains(e.target) && e.target !== els.addr) els.addrList.hidden = true;
});

async function searchAddress(q) {
  const my = ++addrSeq;
  const feats = await fetch(`https://msearch.gsi.go.jp/address-search/AddressSearch?q=${encodeURIComponent(q)}`)
    .then((r) => r.json())
    .catch(() => []);
  if (my !== addrSeq) return;
  els.addrList.replaceChildren();
  for (const f of feats.slice(0, 8)) {
    const [lon, lat] = f.geometry.coordinates;
    const li = document.createElement("li");
    li.textContent = f.properties.title;
    li.addEventListener("click", () => {
      els.addrList.hidden = true;
      els.addr.value = f.properties.title;
      setCenter(L.latLng(lat, lon), { pan: true, zoom: 15 });
    });
    els.addrList.append(li);
  }
  els.addrList.hidden = els.addrList.childElementCount === 0;
}
