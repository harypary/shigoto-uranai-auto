"""note.com ログイン設定（新しいアカウントで最初に1回、またはセッションが切れたときに実行）

  cd C:\\Users\\haryp\\game\\33.shigoto_uranai
  python scripts/setup_note_session.py

ブラウザが開くので、ご自身で note.com にログインしてください。ログインを自動で検知し、次まで行います:
  1. 平文のセッションを output/note_session.json に保存（.gitignore 対象）
  2. 暗号鍵 SESSION_KEY を用意（.env に無ければ生成して .env に追記）
  3. 暗号化したセッションを data/session/note_session.enc に保存
  4. gh が使えれば GitHub の Secret SESSION_KEY と変数 NOTE_USER_ID を登録し、暗号化セッションを commit/push
鍵やCookieの値は画面に表示しない。
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.publishers.session_store import ENCRYPTED_FILE, generate_key, save_encrypted  # noqa: E402

SESSION_FILE = ROOT / "output" / "note_session.json"
ENV_FILE = ROOT / ".env"
REPO = "harypary/shigoto-uranai-auto"
TIMEOUT_SEC = 600


def _current_user(context) -> dict:
    r = context.request.get("https://note.com/api/v2/current_user", headers={"Accept": "application/json"})
    if r.status != 200:
        return {}
    try:
        return r.json().get("data") or {}
    except Exception:
        return {}


def _session_key() -> tuple[str, bool]:
    """.env の SESSION_KEY を返す。無ければ生成して .env に追記する（戻り値の2つ目は新規生成したか）"""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("SESSION_KEY=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip(), False
    key = generate_key()
    with ENV_FILE.open("a", encoding="utf-8") as f:
        f.write(f"\nSESSION_KEY={key}\n")
    return key, True


def _gh(args: list[str], stdin: str | None = None) -> bool:
    try:
        r = subprocess.run(["gh", *args], input=stdin, text=True, capture_output=True, cwd=ROOT)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _git(args: list[str]) -> bool:
    r = subprocess.run(["git", *args], text=True, capture_output=True, cwd=ROOT)
    return r.returncode == 0


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=False)
        except Exception:
            browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto("https://note.com/login")
        print("ブラウザで note.com にログインしてください（最大10分待機）", flush=True)

        user, start = {}, time.time()
        while time.time() - start < TIMEOUT_SEC:
            time.sleep(3)
            try:
                user = _current_user(context)
            except Exception:
                user = {}
            if user.get("urlname"):
                time.sleep(5)  # ログイン後のCookie確定待ち
                break
        if not user.get("urlname"):
            browser.close()
            sys.exit("タイムアウト: ログインを検知できませんでした。もう一度実行してください。")
        state = context.storage_state()
        browser.close()

    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    key, created = _session_key()
    save_encrypted(state, key_b64=key)
    print(f"ログインを確認: {user.get('nickname')}（note.com/{user['urlname']}）")
    print(f"暗号化したセッションを保存: {ENCRYPTED_FILE.relative_to(ROOT)}" + ("（暗号鍵を新規作成して .env に保存）" if created else ""))

    ok_key = _gh(["secret", "set", "SESSION_KEY", "--repo", REPO], stdin=key)
    ok_user = _gh(["variable", "set", "NOTE_USER_ID", "--repo", REPO, "--body", user["urlname"]])
    pushed = (_git(["add", str(ENCRYPTED_FILE.relative_to(ROOT))])
              and (_git(["diff", "--cached", "--quiet"]) or _git(["commit", "-m", "session: 新しいログインを保存"]))
              and _git(["push"]))
    print(f"GitHub Secret SESSION_KEY: {'登録しました' if ok_key else '未登録（gh secret set SESSION_KEY で手動登録）'}")
    print(f"GitHub 変数 NOTE_USER_ID: {'登録しました' if ok_user else '未登録（gh variable set NOTE_USER_ID で手動登録）'}")
    print(f"暗号化セッションの push: {'完了' if pushed else '未完了（git add data/session → commit → push）'}")


if __name__ == "__main__":
    main()
