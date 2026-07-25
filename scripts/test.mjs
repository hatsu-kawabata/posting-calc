// node --test scripts/test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { meshCentroid, primaryMeshesInBBox, circleBBox, aggregateCircle } from "../web/mesh.js";
import { plan, roundUpTo, DEFAULTS, INDUSTRIES } from "../web/calc.js";

const WEB = join(dirname(fileURLToPath(import.meta.url)), "..", "web");

function cellsAround(lat, lon, r) {
  const [latMin, latMax, lonMin, lonMax] = circleBBox(lat, lon, r);
  const cells = [];
  for (const code of primaryMeshesInBBox(latMin, latMax, lonMin, lonMax)) {
    let rows;
    try {
      rows = JSON.parse(readFileSync(join(WEB, "data", `${code}.json`), "utf8"));
    } catch {
      continue;
    }
    for (const [mc, pop, hh] of rows) {
      const [la, lo] = meshCentroid(mc);
      cells.push({ la, lo, pop, hh });
    }
  }
  return cells;
}

const SHINJUKU = { lat: 35.68953, lon: 139.69986 };

test("メッシュ中心の復元: 9桁コード→緯度経度がセル幅の範囲に収まる", () => {
  const [la, lo] = meshCentroid("533945764");
  assert.ok(la > 35.6 && la < 35.8, `lat=${la}`);
  assert.ok(lo > 139.6 && lo < 139.8, `lon=${lo}`);
});

test("新宿駅1km圏の世帯数が商圏メーカーの公開値(17,579世帯)と一致する", () => {
  const cells = cellsAround(SHINJUKU.lat, SHINJUKU.lon, 1000);
  const agg = aggregateCircle(cells, SHINJUKU.lat, SHINJUKU.lon, 1000);
  assert.equal(agg.hh, 17579);
  // 同じ集計器なので人口も一致する(公開値 約24,300人)
  assert.ok(Math.abs(agg.pop - 24300) < 100, `pop=${agg.pop}`);
});

test("半径を広げると世帯数は単調に増える", () => {
  const cells = cellsAround(SHINJUKU.lat, SHINJUKU.lon, 3000);
  let prev = -1;
  for (const r of [300, 500, 1000, 2000, 3000]) {
    const { hh } = aggregateCircle(cells, SHINJUKU.lat, SHINJUKU.lon, r);
    assert.ok(hh > prev, `r=${r} hh=${hh} prev=${prev}`);
    prev = hh;
  }
});

test("皇居の中心は居住世帯がほぼない", () => {
  const lat = 35.6852, lon = 139.7528;
  const cells = cellsAround(lat, lon, 300);
  const { hh } = aggregateCircle(cells, lat, lon, 300);
  assert.ok(hh < 300, `hh=${hh}`);
});

test("データ範囲外(海上)は0で落ちない", () => {
  const lat = 30.0, lon = 150.0;
  const cells = cellsAround(lat, lon, 1000);
  const agg = aggregateCircle(cells, lat, lon, 1000);
  assert.equal(agg.hh, 0);
  assert.equal(agg.cellCount, 0);
});

test("ロット切り上げ", () => {
  assert.equal(roundUpTo(1, 100), 100);
  assert.equal(roundUpTo(100, 100), 100);
  assert.equal(roundUpTo(101, 100), 200);
  assert.equal(roundUpTo(0, 100), 0);
});

test("部数=配布可能世帯×(1+予備率)をロット単位に切り上げ", () => {
  const r = plan({
    households: 10000, coverage: 100, spare: 5,
    unitPrint: 4, unitDeliver: 5, rateLo: 0.1, rateHi: 0.3,
  });
  assert.equal(r.deliverable, 10000);
  assert.equal(r.copies, 10500);
  assert.equal(r.costPrint, 42000);   // 10500部 × 4円
  assert.equal(r.costDeliver, 50000); // 配るのは10000部 × 5円
  assert.equal(r.costTotal, 92000);
});

test("配布可能率は配布部数と配布費に効き、印刷部数にも波及する", () => {
  const r = plan({
    households: 10000, coverage: 80, spare: 0,
    unitPrint: 4, unitDeliver: 5, rateLo: 0.1, rateHi: 0.1,
  });
  assert.equal(r.deliverable, 8000);
  assert.equal(r.copies, 8000);
  assert.equal(r.costDeliver, 40000);
});

test("反響は配った部数に対して起き、CPAは反響が多いほど安い", () => {
  const r = plan({
    households: 10000, coverage: 100, spare: 5,
    unitPrint: 4, unitDeliver: 5, rateLo: 0.1, rateHi: 0.5,
  });
  assert.equal(r.responsesLo, 10);
  assert.equal(r.responsesHi, 50);
  assert.ok(r.cpaLo < r.cpaHi, `${r.cpaLo} < ${r.cpaHi}`);
  assert.equal(Math.round(r.cpaLo), Math.round(r.costTotal / 50));
});

test("世帯数0でもCPAはnullになり例外を出さない", () => {
  const r = plan({
    households: 0, coverage: 100, spare: 5,
    unitPrint: 4, unitDeliver: 5, rateLo: 0.1, rateHi: 0.3,
  });
  assert.equal(r.copies, 0);
  assert.equal(r.costTotal, 0);
  assert.equal(r.cpaLo, null);
  assert.equal(r.cpaHi, null);
});

test("業種テーブルは lo<=hi で、既定値は正の数", () => {
  for (const i of INDUSTRIES) {
    assert.ok(i.lo <= i.hi, `${i.id}: ${i.lo} > ${i.hi}`);
    assert.ok(i.lo > 0, `${i.id}`);
  }
  for (const k of ["coverage", "spare", "unitPrint", "unitDeliver", "lot"]) {
    assert.ok(DEFAULTS[k] >= 0, k);
  }
});
