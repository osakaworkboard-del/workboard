"""work-board.html から Firebase 版の index.html を作る。
- 画面と処理は元のまま。保存先とログインだけを Firebase にする（fb-layer.html）
- 履歴（請求書PDF）は外す
使い方: python3 tools/build.py /home/claude/work-board.html [config.json]
"""
import json, re, sys, pathlib

here = pathlib.Path(__file__).resolve().parent
src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
cfg_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else here.parent / "config.json"
cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {"apiKey": "ここにFirebaseの設定を入れる"}

def rep(text, a, b):
    assert text.count(a) == 1, ("not found / not unique", a[:80])
    return text.replace(a, b)

head_end = src.index("<script>")
page, script = src[:head_end], src[head_end:]

# ---------- 履歴（請求書）を外す ----------
page = rep(page, '<button type="button" id="tabHist" aria-pressed="false">履歴</button>',
           '<button type="button" id="tabHist" aria-pressed="false" hidden>履歴</button>')
s = script
s = rep(s, 'if(v==="m"||v==="p"||v==="h"||v==="r")showTab(v)', 'if(v==="m"||v==="p"||v==="r")showTab(v)')
s = rep(s, 'function renderCardHist(c){const b=$("histBlock");', 'function renderCardHist(c){const b=$("histBlock");b.hidden=true;return;')
s = rep(s, 'db.collection("invoices").onSnapshot(s=>{invoices=new Map(s.docs.map(d=>[d.id,{...d.data(),id:d.id}]));if(!$("histView").hidden)renderHist()},()=>{});', '')
s = rep(s, '（カード${lb.cars||0}件・請求書${lb.invoices||0}件）', '（カード${lb.cars||0}件）')
s = rep(s, '／請求書 ${v.n}件（上書き ${v.over}）<br>', '<br>')
s = rep(s, '・代車予定 ${l.gone}件・請求書 ${v.gone}件', '・代車予定 ${l.gone}件')
s = rep(s, ',["invoices",b.invoices,invoices]]){', ']){')
s = rep(s, 'render();setBanner("local");', 'render();$("btnInvImport").hidden=true;')

layer = (here / "fb-layer.html").read_text(encoding="utf-8")
cfg_js = "<script>window.FB_CONFIG=" + json.dumps(cfg, ensure_ascii=False) + ";</script>\n"
# ログイン部品はヘッダーのすぐ下（バナーの前）に入れる
page = rep(page, '<div class="banner" id="banner" hidden></div>', '<div class="banner" id="banner" hidden></div>\n' + layer)
out = "<!doctype html>\n<html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n" + \
      page.replace("<style>", cfg_js + "<style>", 1).replace("</style>", "</style>\n</head><body>", 1) + s + "\n</body></html>\n"
# 順番の確認：設定 → 約束（window.claude）→ 元のアプリ
assert out.index("window.FB_CONFIG") < out.index("window.__fbReady=ready") < out.index("/* ---------- boot ---------- */")
dst = here.parent / "public" / "index.html"
dst.write_text(out, encoding="utf-8")
print("wrote", dst, len(out), "chars")
