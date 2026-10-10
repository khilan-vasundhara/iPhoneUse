#!/usr/bin/env python3
"""Live iPhone mirror in your browser (works with Claude Code). Usage: python3 scripts/mirror.py [--port 8765]"""
import argparse, json, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from iphone_use import PUAError, Runtime

PAGE = """<!doctype html><meta charset=utf-8><title>iPhone Mirror</title>
<style>body{margin:0;background:#111;color:#ccc;font:14px system-ui;display:flex;flex-direction:column;align-items:center;height:100vh}
#s{margin:8px}#i{max-height:calc(100vh - 70px);border-radius:28px;border:6px solid #333;background:#000}
button{margin:0 4px;padding:6px 12px}</style>
<div id=s>iPhone Mirror - <span id=t>connecting</span>
<button onclick="act('refresh')">Refresh</button><button onclick="act('home')">Home</button></div>
<img id=i alt="">
<script>
let seq=0,img=document.getElementById('i'),t=document.getElementById('t');
async function act(a){await fetch('/api/action?action='+a,{method:'POST'})}
async function loop(){
 try{const r=await (await fetch('/api/frame?after_seq='+seq)).json();
  if(r.error){t.textContent=r.error.message||'error'}
  else if(r.paused){t.textContent='paused'}
  else{const f=r.frame;t.textContent=r.device&&r.device.model?r.device.model+' - live':'live';
   if(f&&f.seq>seq){seq=f.seq;img.src='data:'+f.mimeType+';base64,'+f.data}}
 }catch(e){t.textContent='disconnected'}
 setTimeout(loop,200)}
loop()
</script>"""


def make_handler(runtime):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def send(self, body, ctype):
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def call(self, tool, args):
            try:
                return runtime.call(tool, args)
            except PUAError as exc:
                return {"error": exc.as_dict()}

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/":
                return self.send(PAGE, "text/html; charset=utf-8")
            if url.path == "/api/frame":
                seq = int(parse_qs(url.query).get("after_seq", ["0"])[0])
                return self.send(json.dumps(self.call("pua_screen_frame", {"after_seq": seq})), "application/json")
            self.send_error(404)

        def do_POST(self):
            url = urlparse(self.path)
            action = parse_qs(url.query).get("action", [""])[0]
            if url.path != "/api/action" or action not in ("refresh", "home"):
                return self.send_error(404)
            self.send(json.dumps(self.call("pua_screen_action", {"action": action})), "application/json")
    return H


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-open", action="store_true")
    args = p.parse_args()
    runtime = Runtime()
    # ponytail: binds loopback only; the stream has no auth, so never expose it.
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(runtime))
    url = f"http://127.0.0.1:{args.port}/"
    print("Mirroring at", url, "(Ctrl+C to stop)")
    if not args.no_open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        runtime.close()


if __name__ == "__main__":
    main()
