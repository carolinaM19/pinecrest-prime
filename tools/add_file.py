#!/usr/bin/env python3
"""Encrypt a document (e.g. a warranty PDF) for the website.

Usage: python3 tools/add_file.py <input file> <short-name>
Writes files/<short-name>.bin (encrypted) and prints the JSON to store with the
record in the dashboard ({path, key, iv, type, name, size}). The key only lives
inside the encrypted data, so the file can't be opened without the site password.
"""
import base64, json, mimetypes, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, name = sys.argv[1], sys.argv[2]
raw = open(src, 'rb').read()
key = AESGCM.generate_key(bit_length=256); iv = os.urandom(12)
path = f'files/{name}.bin'
open(os.path.join(root, path), 'wb').write(AESGCM(key).encrypt(iv, raw, None))
b = lambda x: base64.b64encode(x).decode()
print(json.dumps({'path': path, 'key': b(key), 'iv': b(iv),
                  'type': mimetypes.guess_type(src)[0] or 'application/octet-stream',
                  'name': os.path.basename(src), 'size': len(raw)}))
