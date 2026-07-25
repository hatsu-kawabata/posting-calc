# ポスティング部数計算機

配布したい範囲を地図で囲むと、**圏内世帯数 → 必要部数 → 概算費用 → 想定反響件数 → 1件あたり獲得コスト**が
その場で出る無料ツール。登録不要・サーバ計算なし（全てクライアントサイド）。

- データ: 総務省統計局「令和2年国勢調査」500mメッシュ統計（e-Stat 統計GIS）の世帯数・人口
- 計算: `世帯数 × 配布可能率 × (1 + 予備率)` を発注ロット単位に切り上げ。
  配布費は「配る部数」、印刷費は「刷る部数」に掛ける（この2つは一致しない）
- 反響率・単価はいずれも業界公表値の**幅**をそのまま使い、単一値に潰さない

## 商圏メーカーとの関係

[商圏メーカー](https://github.com/hatsu-kawabata/shoken-maker) が「そこに誰が住んでいるか」に答えるのに対し、
本ツールは「**何部刷って・いくらかかって・何件返るか**」に答える。前集計済みメッシュ資産を再利用しており、
`scripts/build_slim_data.py` が商圏メーカーのデータから必要な2列（人口・世帯数）だけを抜いて 67.8MB → 9.3MB に絞る。
新宿駅1km圏の世帯数が商圏メーカーの公開値（17,579世帯）と一致することをテストで固定している。

## 構成

```
scripts/build_slim_data.py  商圏メーカーのメッシュ資産 → 2列slim版(9.3MB)
scripts/gen_articles.py     解説記事3本+一覧+sitemap+robots+llms.txt を生成
scripts/test.mjs            メッシュ集計と部数計算の純関数テスト(11本)
web/mesh.js                 500mメッシュの座標計算と円内集計(純関数)
web/calc.js                 部数・費用・反響・獲得単価の計算(純関数)+業種別反響率テーブル
web/app.js                  地図UI・パラメータ・URL共有
```

## 開発

```sh
python3 scripts/build_slim_data.py   # データ生成(商圏メーカーのweb/dataが必要)
python3 scripts/gen_articles.py      # 記事・sitemap生成
node --test scripts/test.mjs         # テスト
python3 -m http.server 8138 -d web   # ローカル起動 → http://localhost:8138
```

## 出典と免責

- 総務省統計局「令和2年国勢調査」500mメッシュ統計（e-Stat 統計GIS）を加工して作成
- 反響率の目安: [株式会社ウィット](https://wi-t.co.jp/column/posting-response-rate/)
- 配布単価の目安: [株式会社ポスティングサービス](https://postingservice.co.jp/posting-cost-regional-comparison-2025/)
- 数値は概算であり、配布実績・反響を保証するものではありません

MIT License
