"""Immutable folder snapshots, diffs, safe restores, and a local timeline UI."""
import argparse
import difflib
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

class History:
    def __init__(self, folder):
        self.root = Path(folder).resolve()
        if not self.root.is_dir(): raise ValueError('Folder must already exist')
        self.store = self.root / '.time-machine'

    def snapshots(self):
        return sorted((self.store / 'snapshots').glob('*.json'), reverse=True)

    def load(self, revision):
        if not revision or any(c not in '0123456789abcdef-' for c in revision):
            raise ValueError('Invalid revision')
        return json.loads((self.store / 'snapshots' / (revision + '.json')).read_text())

    def snapshot(self, label=''):
        files = {}
        for path in sorted(self.root.rglob('*')):
            relative = path.relative_to(self.root)
            if '.time-machine' in relative.parts or '.git' in relative.parts: continue
            if path.is_symlink() or not path.is_file(): continue
            # Do not follow a directory symlink outside the selected root.
            if any(p.is_symlink() for p in path.parents if p != self.root): continue
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            blob = self.store / 'objects' / digest
            if not blob.exists(): atomic(blob, data)
            files[relative.as_posix()] = digest
        revision = f'{time.time_ns():x}-{os.urandom(4).hex()}'
        atomic(self.store / 'snapshots' / (revision + '.json'),
               json.dumps(dict(id=revision, label=label, created=time.time(), files=files)).encode())
        return revision

    def diff(self, older, newer):
        a, b = self.load(older)['files'], self.load(newer)['files']
        out = []
        for name in sorted(a.keys() | b.keys()):
            if a.get(name) == b.get(name): continue
            out.append(f'FILE {name}: ' + ('added' if name not in a else 'deleted' if name not in b else 'changed'))
            try:
                read = lambda d: (self.store / 'objects' / d).read_bytes().decode('utf-8').splitlines(True) if d else []
                out.extend(difflib.unified_diff(read(a.get(name)), read(b.get(name)), fromfile='old/'+name, tofile='new/'+name))
            except UnicodeDecodeError: out.append('Binary file changed\n')
        return '\n'.join(out)

    def restore(self, revision, destination):
        dest = Path(destination).resolve()
        # Restores never overwrite an existing directory, including the source.
        dest.mkdir(parents=True, exist_ok=False)
        for name, digest in self.load(revision)['files'].items():
            path = dest / name
            if not path.resolve().is_relative_to(dest): raise ValueError('Unsafe stored path')
            if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                raise ValueError('Invalid object hash')
            data = (self.store / 'objects' / digest).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest: raise ValueError('Corrupted object')
            atomic(path, data)

    def serve(self, port):
        history = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                rows = []
                for path in history.snapshots():
                    item = json.loads(path.read_text())
                    rows.append('<li><strong>'+html.escape(item['label'] or 'Untitled')+'</strong><br><code>'+item['id']+'</code> · '+str(len(item['files']))+' files</li>')
                body = ('<!doctype html><meta charset="utf-8"><title>Time Machine</title><style>body{background:#101827;color:#e5eefb;font:18px system-ui;max-width:900px;margin:60px auto}li{border-left:3px solid #5eead4;padding:20px;margin:20px}code{font-size:14px}</style><h1>Folder time machine</h1><p>'+html.escape(str(history.root))+'</p><ol>'+''.join(rows)+'</ol>').encode()
                self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(body)
        print(f'Timeline: http://127.0.0.1:{port}')
        HTTPServer(('127.0.0.1',port),Handler).serve_forever()

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('folder')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('snapshot'); s.add_argument('--label',default='')
    sub.add_parser('list')
    d=sub.add_parser('diff'); d.add_argument('older'); d.add_argument('newer')
    r=sub.add_parser('restore'); r.add_argument('revision'); r.add_argument('destination')
    w=sub.add_parser('serve'); w.add_argument('--port',type=int,default=8080)
    a=p.parse_args(); h=History(a.folder)
    if a.command=='snapshot': print(h.snapshot(a.label))
    elif a.command=='list':
        for s in h.snapshots(): print(s.stem, json.loads(s.read_text())['label'])
    elif a.command=='diff': print(h.diff(a.older,a.newer))
    elif a.command=='restore': h.restore(a.revision,a.destination)
    else: h.serve(a.port)
if __name__=='__main__': main()
