// 配布計画の計算。純関数のみ(nodeテスト可能)。
//
// 設計方針: 数字を作らない。既定値はすべて出典のある「目安」で、UIから変更できる。
// 出典が幅で示されているものは幅のまま扱い、単一値に潰さない（早すぎるスカラー化をしない）。

// 業種別の反響率(%)。出典: 株式会社ウィット「ポスティング反響率の計算方法は？業種別の平均値」
// https://wi-t.co.jp/column/posting-response-rate/
export const INDUSTRIES = [
  { id: "food", label: "飲食店・デリバリー", lo: 0.3, hi: 0.5 },
  { id: "retail", label: "小売（スーパー・ドラッグストア等）", lo: 0.1, hi: 0.5 },
  { id: "beauty", label: "美容（サロン等）", lo: 0.1, hi: 0.2 },
  { id: "gym", label: "スポーツジム", lo: 0.1, hi: 0.3 },
  { id: "ec", label: "通販（化粧品・健康食品等）", lo: 0.05, hi: 0.3 },
  { id: "care", label: "介護・福祉サービス", lo: 0.05, hi: 0.2 },
  { id: "medical", label: "医療・福祉", lo: 0.2, hi: 0.2, note: "出典の表記は「0.2%前後」" },
  { id: "school", label: "学習塾", lo: 0.01, hi: 0.03 },
  { id: "estate", label: "不動産", lo: 0.01, hi: 0.03 },
  { id: "reform", label: "リフォーム", lo: 0.01, hi: 0.03 },
  { id: "shigyo", label: "士業（弁護士・税理士等）", lo: 0.01, hi: 0.05 },
  { id: "other", label: "その他・未定", lo: 0.01, hi: 0.5, note: "上記業種の幅を包む範囲。公表値ではない" },
];

// 既定値。単価の出典は articles/cost.html に明記する。
export const DEFAULTS = {
  coverage: 100,    // 配布可能率(%) 既定は世帯数そのまま＝仮定を勝手に置かない
  spare: 5,         // 予備率(%) 端数・破損分の上乗せ
  unitPrint: 4,     // 印刷単価(円/部) A4片面カラー5,000部の目安
  unitDeliver: 5,   // 配布単価(円/部) ローラー3〜6円・セグメント5〜10円の中位
  lot: 100,         // 発注ロット(部) この単位に切り上げる
};

export function roundUpTo(n, lot) {
  if (!(lot > 0)) return Math.ceil(n);
  return Math.ceil(n / lot) * lot;
}

/**
 * 配布計画を計算する。
 * @param {object} p
 * @param {number} p.households 圏内世帯数（メッシュ集計値）
 * @param {number} p.coverage   配布可能率(%)
 * @param {number} p.spare      予備率(%)
 * @param {number} p.unitPrint  印刷単価(円/部)
 * @param {number} p.unitDeliver 配布単価(円/部)
 * @param {number} p.rateLo     反響率の下限(%)
 * @param {number} p.rateHi     反響率の上限(%)
 * @param {number} [p.lot]      発注ロット(部)
 */
export function plan(p) {
  const lot = p.lot ?? DEFAULTS.lot;
  const deliverable = Math.round(p.households * (p.coverage / 100));
  const copies = roundUpTo(deliverable * (1 + p.spare / 100), lot);
  const costPrint = Math.round(copies * p.unitPrint);
  const costDeliver = Math.round(deliverable * p.unitDeliver); // 配布費は実際に配る部数にかかる
  const costTotal = costPrint + costDeliver;

  // 反響は「配った部数」に対して起きる（刷った部数ではない）
  const responsesLo = deliverable * (p.rateLo / 100);
  const responsesHi = deliverable * (p.rateHi / 100);

  return {
    deliverable,
    copies,
    costPrint,
    costDeliver,
    costTotal,
    responsesLo,
    responsesHi,
    // 1件あたり獲得コスト: 反響が多いほど安くなるので lo/hi が入れ替わる
    cpaLo: responsesHi > 0 ? costTotal / responsesHi : null,
    cpaHi: responsesLo > 0 ? costTotal / responsesLo : null,
  };
}

export function fmtYen(n) {
  return "¥" + Math.round(n).toLocaleString("ja-JP");
}

export function fmtRange(lo, hi, digits = 1) {
  const f = (v) => v.toFixed(digits);
  return lo === hi ? f(lo) : `${f(lo)}〜${f(hi)}`;
}
