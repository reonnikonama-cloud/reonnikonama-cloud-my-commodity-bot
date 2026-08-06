import json
import urllib.request


def send_discord_message(
    url: str, message: str = None, embed: dict = None
):
    """指定されたWebhook URLへメッセージまたはEmbedを送信"""
    if not url:
        print(
            "[WARN] Webhook URLが未設定のためメッセージ送信をスキップします。"
        )
        return

    payload = {}
    if message:
        payload["content"] = message
    if embed:
        payload["embeds"] = [embed]

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            if res.status in (200, 204):
                print("[INFO] Discord通知送信完了")
            else:
                print(f"[WARN] Discord通知応答コード: {res.status}")
    except Exception as e:
        print(f"[ERROR] Discord通知送信失敗: {e}")
