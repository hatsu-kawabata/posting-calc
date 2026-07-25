"""商圏メーカーの前集計メッシュから、部数計算に必要な列だけを抜いたslim版を作る。

入力: ~/shoken_maker/web/data/{1次メッシュ}.json  行= [code, 総数, 男, 女, 世帯, 平均年齢, b0m..b19f]
出力: ~/posting_calc/web/data/{1次メッシュ}.json   行= [code, 総数, 世帯数]

e-Statへの再取得はしない(加工済み資産の再利用)。数値は変換せず列を落とすだけ。
世帯数がnull(秘匿)のセルはnullのまま残し、UI側で「秘匿セルあり」として開示する。
"""
import json
from pathlib import Path

SRC = Path.home() / "shoken_maker" / "web" / "data"
DST = Path(__file__).resolve().parent.parent / "web" / "data"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    src_manifest = json.loads((SRC / "manifest.json").read_text())
    # 対象は manifest が列挙する1次メッシュのファイルだけ(stations.json 等の同居ファイルを拾わない)
    files = [SRC / f"{m}.json" for m in src_manifest["meshes"]]
    missing = [p.name for p in files if not p.exists()]
    if missing:
        raise SystemExit(f"missing source files: {missing[:5]}")

    cells = pop = hh = masked = 0
    for f in files:
        rows = json.loads(f.read_text())
        slim = [[r[0], r[1], r[4]] for r in rows]
        (DST / f.name).write_text(json.dumps(slim, separators=(",", ":")))
        cells += len(slim)
        pop += sum(r[1] for r in slim if r[1] is not None)
        hh += sum(r[2] for r in slim if r[2] is not None)
        masked += sum(1 for r in slim if r[2] is None)

    (DST / "manifest.json").write_text(json.dumps({
        "format": 1,
        "derivedFrom": "shoken-maker web/data (format %s)" % src_manifest.get("format"),
        "source": src_manifest.get("source"),
        "columns": ["meshCode", "population", "households"],
        "meshes": src_manifest.get("meshes"),
    }, ensure_ascii=False, separators=(",", ":")))

    src_mb = sum(f.stat().st_size for f in files) / 1e6
    dst_mb = sum(p.stat().st_size for p in DST.glob("*.json") if p.name != "manifest.json") / 1e6
    print(f"{len(files)} files / {cells:,} cells / 世帯数秘匿 {masked} cells")
    print(f"総人口 {pop:,} / 総世帯 {hh:,}")
    print(f"{src_mb:.1f}MB -> {dst_mb:.1f}MB ({dst_mb/src_mb:.0%})")


if __name__ == "__main__":
    main()
