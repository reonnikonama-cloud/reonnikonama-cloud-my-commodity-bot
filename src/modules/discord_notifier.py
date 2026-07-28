from discord import SyncWebhook, Embed

def send_webhook(webhook_url: str, embed: Embed, system_log_url: str = ""):
    if not webhook_url:
        print("[WARN] Webhook URLが設定されていないため通知をスキップします。")
        return

    try:
        webhook = SyncWebhook.from_url(webhook_url)
        webhook.send(embed=embed)
        print("[SUCCESS] Discord通知送信完了！")
    except Exception as e:
        err_msg = f"[ERROR] Discord送信失敗: {e}"
        print(err_msg)
        if system_log_url and system_log_url != webhook_url:
            try:
                sys_webhook = SyncWebhook.from_url(system_log_url)
                sys_webhook.send(content=f"🚨 **システムエラーが発生しました**\n```{err_msg}```")
            except Exception:
                pass
