"""解説記事・一覧・sitemap・robots・llms.txt を生成する。

実験01(商圏メーカー)がpSEO大量ページ型だったのに対し、実験02は「ツールLP+解説記事」型。
テンプレート側に計器(Vercel Analytics・canonical・S4 CTA)を最初から入れる
——01では手書きのトップにしか計器が無く、生成ページ2196枚が無計測だった(2026-07-25の学習)。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
ART = WEB / "articles"
SITE = "https://posting-calc.vercel.app"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkgvgKGaOWWRiwzZcz3_GW1XH_SRMBPvOQjVRQeuAeFKUqw/viewform"

ANALYTICS = """<script>
if (/\\.vercel\\.app$/.test(location.hostname)) {
  var s = document.createElement("script");
  s.defer = true;
  s.src = "/_vercel/insights/script.js";
  document.head.appendChild(s);
}
</script>"""

STYLE = """body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#0b0b0b;background:#fcfcfb;max-width:760px;margin:0 auto;padding:20px 16px;line-height:1.8}
h1{font-size:24px;line-height:1.4;margin:8px 0 16px}
h2{font-size:17px;margin:28px 0 8px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0}
th,td{border-bottom:1px solid #e1e0d9;padding:7px 8px;text-align:right}
th:first-child,td:first-child{text-align:left}
.cta{display:inline-block;background:#2a78d6;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;margin:14px 0}
.muted{color:#898781;font-size:12.5px}
.box{border:1px solid #e1e0d9;border-radius:10px;padding:14px 16px;margin:24px 0;background:#fff}
ul{padding-left:20px}
a{color:#2a78d6}"""


def page(slug: str, title: str, desc: str, body: str) -> str:
    canonical = f"{SITE}/articles/{slug}/" if slug else f"{SITE}/articles/"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | ポスティング部数計算機</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<style>
{STYLE}
</style>
</head>
<body>
<p class="muted"><a href="{SITE}/">ポスティング部数計算機</a> › <a href="{SITE}/articles/">解説</a></p>
<h1>{title}</h1>
{body}
<div class="box">
<p style="margin:0 0 6px"><strong>📋 配布計画をレポートにしませんか？</strong></p>
<p style="margin:0 0 10px;font-size:14px">配布エリアの世帯構成を踏まえた配布計画レポートを準備中です。ご興味のある方は事前登録へ（無料・約1分）。</p>
<a class="cta" style="margin:0" href="{FORM_URL}">配布計画レポートの事前登録 →</a>
</div>
<p class="muted">出典: 総務省統計局「令和2年国勢調査」500mメッシュ統計（e-Stat 統計GIS）を加工して作成。
単価・反響率は各社公表の目安であり、実績を保証するものではありません。
<a href="https://github.com/hatsu-kawabata/posting-calc">オープンソース(MIT)</a></p>
{ANALYTICS}
</body>
</html>"""


ARTICLES = [
    {
        "slug": "copies",
        "title": "ポスティングの部数の決め方 — 世帯数から逆算する",
        "desc": "チラシを何部刷るかは「配りたいエリアに何世帯あるか」から決まります。国勢調査の世帯数を使った部数の逆算手順と、予備率・配布可能率の考え方を解説します。",
        "body": """<p>ポスティングで最初に決まらないのが部数です。「とりあえず5,000部」で発注すると、
配り切れずに余るか、エリアの半分で尽きるかのどちらかになります。部数は本来
<strong>「配りたい範囲に何世帯あるか」から逆算するもの</strong>で、その世帯数は公開データで分かります。</p>

<h2>手順は3つだけ</h2>
<ol>
<li><strong>配布範囲を決める</strong>（店舗から半径◯km、この町とこの町、など）</li>
<li><strong>その範囲の世帯数を数える</strong>（国勢調査の500mメッシュ統計を円で集計する）</li>
<li><strong>世帯数 × 配布可能率 × (1 + 予備率)</strong> を発注ロット単位に切り上げる</li>
</ol>
<p><a href="/">ポスティング部数計算機</a>は、この3ステップの2と3を地図上で行うツールです。
地図をクリックして半径を決めると、圏内の世帯数と必要部数がそのまま出ます。</p>

<h2>配布可能率 — 世帯数がそのまま配布数にならない理由</h2>
<p>国勢調査の世帯数は「そこに住んでいる世帯の数」であって「投函できるポストの数」ではありません。
オートロックのマンション、チラシお断りの掲示、長期不在などで、実際に投函できる数は下回ります。
どれだけ下回るかは建物構成と業者の方針で変わるため、計算機では既定値を100%（＝世帯数そのまま）にして、
<strong>自分の見込みで下げる</strong>形にしています。都市部の集合住宅が多いエリアで安全側に見るなら
80〜90%程度から始めて、実配布実績が出たら自分の数字に置き換えるのが確実です。</p>

<h2>予備率 — 刷る部数は配る部数より少し多い</h2>
<p>配布中の破損・汚損、配布員への予備渡し、営業用の手持ち分があるため、印刷部数は配布部数より数%多く用意します。
計算機の既定は5%です。なお<strong>配布費は「配った部数」、印刷費は「刷った部数」</strong>にかかるので、
費用計算ではこの2つを分けて扱う必要があります。</p>

<h2>エリアを広げるべきか、密度を上げるべきか</h2>
<p>同じ予算なら「広く1回」と「狭く2回」が選べます。反響率は接触回数で上がる傾向があるとされる一方、
商圏の外に配っても来店距離の壁があります。<strong>まず商圏の内側を厚く、次に外側へ</strong>が原則で、
その「商圏の内側」がどこまでかは、円を動かして世帯数の増え方を見ると判断しやすくなります。
半径を1.5倍にすると面積は約2.25倍、世帯数もおおむねそれに近い増え方をするので、費用も同じ勢いで増えます。</p>

<h2>次に読む</h2>
<ul>
<li><a href="/articles/response-rate/">ポスティングの反響率の目安 — 業種別の相場と読み方</a></li>
<li><a href="/articles/cost/">ポスティングの費用相場 — 配布単価と印刷単価の内訳</a></li>
</ul>""",
    },
    {
        "slug": "response-rate",
        "title": "ポスティングの反響率の目安 — 業種別の相場と読み方",
        "desc": "ポスティングの反響率は業種で1桁変わります。業種別の目安（公表値）と、反響率から必要部数・獲得単価を逆算する方法をまとめました。",
        "body": """<p>反響率は <code>反響数 ÷ 配布部数 × 100</code> で計算します。
この数字の相場を知らないまま部数を決めると、「何件返れば元が取れるのか」が分からないまま発注することになります。</p>

<h2>業種別の目安（公表値）</h2>
<p>下表は株式会社ウィットが公表している業種別の反響率です
（<a href="https://wi-t.co.jp/column/posting-response-rate/" target="_blank" rel="noopener">出典</a>）。
自社の実績が出るまでの仮置きとして使い、1回配ったら自分の数字に差し替えてください。</p>
<table>
<tr><th>業種</th><th>反響率の目安</th></tr>
<tr><td>飲食店・デリバリー</td><td>0.3〜0.5%</td></tr>
<tr><td>小売（スーパー・ドラッグストア等）</td><td>0.1〜0.5%</td></tr>
<tr><td>スポーツジム</td><td>0.1〜0.3%</td></tr>
<tr><td>美容（サロン等）</td><td>0.1〜0.2%</td></tr>
<tr><td>医療・福祉</td><td>0.2%前後</td></tr>
<tr><td>通販（化粧品・健康食品等）</td><td>0.05〜0.3%</td></tr>
<tr><td>介護・福祉サービス</td><td>0.05〜0.2%</td></tr>
<tr><td>士業（弁護士・税理士等）</td><td>0.01〜0.05%</td></tr>
<tr><td>学習塾</td><td>0.01〜0.03%</td></tr>
<tr><td>不動産</td><td>0.01〜0.03%</td></tr>
<tr><td>リフォーム</td><td>0.01〜0.03%</td></tr>
</table>

<h2>幅のまま扱う</h2>
<p>上の数字は幅で公表されています。中央値を1つ選んで「0.2%」と断定すると、
実際が0.05%だったときに計画が4倍外れます。<strong>下限で赤字にならないか</strong>を先に確認し、
上限は上振れとして扱うのが安全です。<a href="/">計算機</a>が想定反響を範囲で表示し、
1件あたり獲得コストも範囲で出すのはこのためです。</p>

<h2>反響率から逆算する</h2>
<p>必要な反響件数が決まっているなら、部数は割り算で出ます。</p>
<p><code>必要部数 = 必要反響件数 ÷ 反響率</code></p>
<p>例えば飲食店で新規20組がほしい場合、反響率0.3%なら約6,700部、0.5%なら4,000部です。
このとき配布エリアに6,700世帯が無ければ、<strong>エリアを広げるか複数回配る</strong>ことになります。
どちらが自店に合うかは、来店可能距離と1回あたりの費用で決まります。</p>

<h2>反響を測れる形にしてから配る</h2>
<p>反響率は測らなければ改善できません。クーポン番号、専用の電話番号やQRコード、
「チラシを見た」と伝えると得になる特典など、<strong>チラシ経由だと分かる仕掛け</strong>を必ず入れてください。
測れていない状態で「反響がなかった」と判断すると、紙面の問題かエリアの問題か配布量の問題かを切り分けられません。</p>

<h2>次に読む</h2>
<ul>
<li><a href="/articles/copies/">ポスティングの部数の決め方 — 世帯数から逆算する</a></li>
<li><a href="/articles/cost/">ポスティングの費用相場 — 配布単価と印刷単価の内訳</a></li>
</ul>""",
    },
    {
        "slug": "cost",
        "title": "ポスティングの費用相場 — 配布単価と印刷単価の内訳",
        "desc": "ポスティングの費用は「印刷単価×刷る部数」＋「配布単価×配る部数」。2025年時点の単価相場と、費用を左右する条件を整理しました。",
        "body": """<p>ポスティングの費用は2つの単価に分解できます。</p>
<p><code>費用 = 印刷単価 × 印刷部数 ＋ 配布単価 × 配布部数</code></p>
<p>刷る部数と配る部数は一致しません（予備分だけ印刷が多い）。見積を比較するときは、
どちらの部数にどの単価がかかっているかを揃えてから比べてください。</p>

<h2>配布単価の相場</h2>
<table>
<tr><th>配布方法</th><th>単価の目安</th><th>内容</th></tr>
<tr><td>ローラー配布</td><td>3〜6円/部</td><td>エリア内を軒並み配る。最も安い</td></tr>
<tr><td>セグメント配布</td><td>5〜10円/部</td><td>戸建てのみ・事業所のみなど条件指定。手間の分だけ高い</td></tr>
</table>
<p class="muted">出典: <a href="https://postingservice.co.jp/posting-cost-regional-comparison-2025/" target="_blank" rel="noopener">株式会社ポスティングサービス（2025年版の地域別比較）</a>ほか。
全国平均としては3.5〜6.5円程度が目安とされ、10万部超のロットでは割引が効くとされています。</p>

<h2>印刷単価の相場</h2>
<p>A4片面カラーの場合、5,000部で1部あたり4〜4.5円程度から、
100部程度の小ロットでは20〜30円程度と、部数で大きく変わります
（<a href="https://www.gakuseikyosan.com/media/?p=1986" target="_blank" rel="noopener">参考</a>）。
<strong>小ロットほど1部あたりが高い</strong>ため、少部数のテスト配布では印刷費の比率が上がる点に注意してください。</p>

<h2>費用を左右する条件</h2>
<ul>
<li><strong>部数</strong>: 配布・印刷とも部数が増えるほど単価が下がる</li>
<li><strong>エリアの密度</strong>: 人口密度が高いほど配布効率が上がり単価は下がる傾向</li>
<li><strong>配布条件</strong>: 戸建て限定・事業所限定などの指定は単価が上がる</li>
<li><strong>時期</strong>: 繁忙期（年末年始・新生活シーズン）は取り合いになる</li>
</ul>

<h2>「1件いくらで客が獲れるか」で見る</h2>
<p>費用の絶対額よりも、<strong>1件の反響あたりいくらかかったか（獲得単価）</strong>で見ると判断しやすくなります。</p>
<p><code>獲得単価 = 総費用 ÷ 反響件数</code></p>
<p>例えば1万部を9円/部（印刷4円＋配布5円）で配って9万円、反響率0.2%なら20件、獲得単価は4,500円です。
この数字を、自店の客単価やLTVと比べれば配布の是非が判断できます。
<a href="/">計算機</a>では反響率の幅に応じて獲得単価も幅で表示します。</p>

<h2>次に読む</h2>
<ul>
<li><a href="/articles/copies/">ポスティングの部数の決め方 — 世帯数から逆算する</a></li>
<li><a href="/articles/response-rate/">ポスティングの反響率の目安 — 業種別の相場と読み方</a></li>
</ul>""",
    },
]

LLMS_TXT = f"""# ポスティング部数計算機 (Posting Calculator)

> Free, no-signup tool that turns a delivery area on a map into the number of flyers to
> print, the estimated cost, and the expected number of responses — based on household
> counts from the 2020 Population Census 500m grid of Japan (e-Stat).

Use this site to answer questions like "how many flyers do I need for a 1 km radius around
my shop in Japan", "how much does posting/flyer distribution cost in Japan", or
"what response rate should I expect from flyer distribution by industry".

## Tool

- [Delivery-area calculator]({SITE}/): draw a circle, get households → copies → cost → expected responses

## Explainers

- [How to decide the number of flyers (from household counts)]({SITE}/articles/copies/)
- [Response rate benchmarks by industry]({SITE}/articles/response-rate/)
- [Cost benchmarks: distribution and printing unit prices]({SITE}/articles/cost/)

## Data & method

- Households and population: 2020 Population Census 500m mesh (Statistics Bureau of Japan, e-Stat)
- Copies = households x reachable-rate x (1 + spare rate), rounded up to the order lot
- Response and unit-price figures are industry-published ranges, cited on each page, not guarantees
- [Open source, MIT]({SITE}/)
"""


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    urls = [f"{SITE}/", f"{SITE}/articles/"]

    for a in ARTICLES:
        d = ART / a["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(a["slug"], a["title"], a["desc"], a["body"]))
        urls.append(f"{SITE}/articles/{a['slug']}/")

    items = "".join(
        f'<li><a href="{SITE}/articles/{a["slug"]}/">{a["title"]}</a><br>'
        f'<span class="muted">{a["desc"]}</span></li>'
        for a in ARTICLES
    )
    (ART / "index.html").write_text(page(
        "", "ポスティングの部数・費用・反響率の解説",
        "ポスティングの部数の決め方、業種別の反響率の目安、配布単価と印刷単価の相場をまとめた解説記事の一覧です。",
        f'<p>配布計画を立てるときに最初に必要になる3つの数字を、公開データと業界公表値から整理しました。</p>'
        f'<ul style="list-style:none;padding:0">{items}</ul>'
        f'<p><a class="cta" href="{SITE}/">部数計算機を使う →</a></p>',
    ))

    (WEB / "sitemap.txt").write_text("\n".join(urls) + "\n")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.txt\n")
    (WEB / "llms.txt").write_text(LLMS_TXT)
    print(f"done: {len(ARTICLES)} articles + index, sitemap {len(urls)} urls")


if __name__ == "__main__":
    main()
