"""S4フォーム（配布計画レポート事前登録）に設問を追加する。

MCPのFormsツールは create/get/list_responses のみで batchUpdate が無いため、
保存済みOAuth認証情報からアクセストークンを作ってAPIを直接叩く。
Claude Code側は認証情報の読み取りが権限分類器にブロックされるため、株主が手で実行する:

    python3 ~/posting_calc/scripts/add_form_questions.py

冪等ではない（実行するたび設問が増える）。1回だけ実行すること。
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

FORM_ID = "1PWDhrY7bmSetgsTBhPh24xPeiZ-9PIh2JH-UrLrGHs4"
CRED = Path.home() / ".google_workspace_mcp/credentials-personal/exinit0000@gmail.com.json"

DESCRIPTION = (
    "配布エリアの世帯構成をふまえた配布計画レポートを準備中です。"
    "ご登録いただいた方から順にご案内します（無料・約1分）。"
    "※現在は準備中のため、すぐの納品はできません。"
)

QUESTIONS = [
    ("業種", "例: 飲食店 / 美容サロン / 学習塾 / リフォーム", True, False),
    ("配布したいエリア", "住所・駅名など（例: 世田谷区三軒茶屋 / 新宿駅から1km）", True, False),
    ("メールアドレス", "ご案内の送付先", True, False),
    ("想定している配布時期", "例: 2か月以内 / 未定（任意）", False, False),
    ("ご相談内容", "配布部数の悩み、これまでの配布実績など（任意）", False, True),
]


def access_token() -> str:
    cred = json.loads(CRED.read_text())
    body = urllib.parse.urlencode({
        "client_id": cred["client_id"],
        "client_secret": cred["client_secret"],
        "refresh_token": cred["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body) as r:
        return json.load(r)["access_token"]


def main() -> None:
    requests = [{
        "updateFormInfo": {
            "info": {"description": DESCRIPTION},
            "updateMask": "description",
        }
    }]
    for i, (title, desc, required, paragraph) in enumerate(QUESTIONS):
        requests.append({
            "createItem": {
                "item": {
                    "title": title,
                    "description": desc,
                    "questionItem": {
                        "question": {
                            "required": required,
                            "textQuestion": {"paragraph": paragraph},
                        }
                    },
                },
                "location": {"index": i},
            }
        })

    req = urllib.request.Request(
        f"https://forms.googleapis.com/v1/forms/{FORM_ID}:batchUpdate",
        data=json.dumps({"requests": requests}).encode(),
        headers={
            "Authorization": f"Bearer {access_token()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        json.load(r)

    with urllib.request.urlopen(urllib.request.Request(
        f"https://forms.googleapis.com/v1/forms/{FORM_ID}",
        headers={"Authorization": f"Bearer {access_token()}"},
    )) as r:
        form = json.load(r)
    print("設問:", [i.get("title") for i in form.get("items", [])])
    print("回答URL:", form.get("responderUri"))


if __name__ == "__main__":
    main()
