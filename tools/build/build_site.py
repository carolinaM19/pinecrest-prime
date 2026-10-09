#!/usr/bin/env python3
"""Turn the Claude dashboard page into the view-only website (index.html).
Usage: python3 tools/build/build_site.py <dashboard.html>"""
import os, sys
root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(sys.argv[1]).read()
te=src.index('</title>')+8
head=src[:te];rest=src[te:];se=rest.index('</style>')+8;style=rest[:se];body=rest[se:]
def rep(a,b):
    global body
    assert a in body,a[:70];body=body.replace(a,b,1)
extra_css="""<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0}
[hidden]{display:none!important}
img{max-width:100%}
.login{min-height:100vh;display:grid;place-items:center;padding:16px;background:var(--bg)}
.login-card{width:100%;max-width:380px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:28px 24px;display:grid;gap:14px}
.login-card form{display:grid;gap:10px}
.login-card input[type=password]{font-size:16px;padding:10px 12px}
.login-card button{font:600 15px var(--f-body);padding:11px;border-radius:8px;border:0;background:var(--accent);color:var(--accent-fg);cursor:pointer}
.whobar{display:flex;gap:10px;align-items:center;justify-content:flex-end;font-size:12.5px;color:var(--muted)}
#addOther,#addTransfer,#addVendor,#addExpense,#tab-import,#v-import{display:none!important}
button.cell:disabled{opacity:1;cursor:default}
</style>"""
login="""<div class="login" id="login" hidden>
  <div class="login-card">
    <h1>Pinecrest Prime LLC</h1>
    <p class="muted" style="margin:0">Enter the password to see Luca’s income, house expenses and documents.</p>
    <form id="loginForm">
      <label class="f" for="loginPw">Password</label>
      <input id="loginPw" type="password" autocomplete="current-password" required>
      <label class="row small" style="gap:6px;font-weight:500"><input type="checkbox" id="remember"> Keep me signed in on this device</label>
      <button id="loginBtn" type="submit">Open</button>
    </form>
    <p class="small" id="loginMsg" style="margin:0" role="status"></p>
  </div>
</div>
<div id="appwrap" hidden>
"""
rep('<div class="syncbox" id="syncbox">Connecting…</div>','<div><div class="syncbox" id="syncbox">Loading…</div><div class="whobar"><span>View only</span><button class="link" id="signout" type="button">Lock</button></div></div>')
rep('<div class="wrap">',login+'<div class="wrap">')
rep('<div class="toast" id="toast" hidden></div>','</div>\n<div class="toast" id="toast" hidden></div>')
i=body.index('<script>');body=body[:i]+'<script src="unlock.js"></script>\n'+body[i:]
rep("e=e||{};if(!canWrite&&!e.id)return;","e=e||{};if(!canWrite)return;")
rep("$('#syncbox').textContent=parts.join(' · ')||","if(window.__publishedAt)parts.unshift('Updated '+new Date(window.__publishedAt).toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}));$('#syncbox').textContent=parts.join(' · ')||")
rep("if(!window.claude||!window.claude.use){$('#syncbox').textContent='Open this page in Claude to see the ledger.';return}","if(!window.claude||!window.claude.use){return}")
rep("if(!db){$('#syncbox').textContent='Sign in to Claude to see the ledger.';return}","if(!db){return}")
rep("Tap a month name to see that month’s details below, or tap a box to record or change a payment.","Tap a month name to see that month’s details below.")
html='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="robots" content="noindex,nofollow">\n'+head+'\n'+style+extra_css+'\n</head>\n<body>\n'+body+'\n</body>\n</html>\n'
open(os.path.join(root,'index.html'),'w').write(html)
print('index.html built')
