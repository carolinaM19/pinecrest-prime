#!/usr/bin/env python3
"""Encrypt the dashboard data and write data.enc.json.

Usage: python3 tools/publish.py <export_dir>
  <export_dir> holds one folder per collection with one JSON file per record
  (the layout ArtifactData 'list' with out_dir produces).

Only the PUBLIC key (keys.json) is needed here, so no password is required to
publish. The website decrypts in the browser with the private key, which is
itself locked with the site password.
"""
import base64, glob, json, os, sys, datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
data = {}
for col in sorted(os.listdir(src)):
    p = os.path.join(src, col)
    if not os.path.isdir(p):
        continue
    rows = []
    for f in sorted(glob.glob(os.path.join(p, '*.json'))):
        d = json.load(open(f))
        rows.append({'id': d.get('id', os.path.basename(f)[:-5]), **d.get('data', d)})
    data[col] = rows
import hashlib
body = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
digest = hashlib.sha256(body).hexdigest()
out_path = os.path.join(root, 'data.enc.json')
if os.path.exists(out_path) and json.load(open(out_path)).get('contentHash') == digest:
    print('No changes since the last publish; nothing written.')
    sys.exit(0)
payload = json.dumps({'collections': data,
                      'publishedAt': datetime.datetime.now(datetime.timezone.utc).isoformat()},
                     ensure_ascii=False, separators=(',', ':')).encode()

keys = json.load(open(os.path.join(root, 'keys.json')))
pub = serialization.load_der_public_key(base64.b64decode(keys['publicKey']))
k = AESGCM.generate_key(bit_length=256)
iv = os.urandom(12)
ct = AESGCM(k).encrypt(iv, payload, None)
wrapped = pub.encrypt(k, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
out = {'v': 1, 'contentHash': digest, 'wrappedKey': base64.b64encode(wrapped).decode(), 'iv': base64.b64encode(iv).decode(),
       'ciphertext': base64.b64encode(ct).decode()}
json.dump(out, open(out_path, 'w'))
print('wrote data.enc.json:', sum(len(v) for v in data.values()), 'records,', len(payload), 'bytes')
